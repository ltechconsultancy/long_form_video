import os
import httpx
from pathlib import Path

from app.tasks.celery_app import celery_app
from app.services.fal_service import FalService
from app.services.video_service import VideoService
from app.database import SessionLocal
from app.models import Project, Scene

UPLOADS_PATH = Path(os.getenv("UPLOADS_PATH", "/app/uploads"))


def download_file(url: str, output_path: Path) -> Path:
    """Download a file from URL to local path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=300) as client:
        response = client.get(url)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
    return output_path


@celery_app.task(bind=True)
def generate_project_video(self, project_id: int):
    """
    Generate full video for a project by:
    1. Generating images for each scene (via fal.ai)
    2. Generating video clips for each scene (via fal.ai)
    3. Stitching all clips + audio into final video (via FFmpeg)
    """
    db = SessionLocal()
    fal_service = FalService()
    video_service = VideoService(str(UPLOADS_PATH))

    try:
        # Load project and scenes
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {"status": "failed", "error": "Project not found"}

        scenes = (
            db.query(Scene)
            .filter(Scene.project_id == project_id)
            .order_by(Scene.order)
            .all()
        )

        if not scenes:
            project.status = "failed"
            db.commit()
            return {"status": "failed", "error": "No scenes in project"}

        project.status = "generating"
        db.commit()

        self.update_state(state="PROCESSING", meta={"step": "generating_images", "progress": 0})

        video_clips = []
        total_scenes = len(scenes)

        for i, scene in enumerate(scenes):
            progress = int((i / total_scenes) * 100)

            # Step 1: Generate or use existing image
            if scene.reference_image_path:
                # Upload reference image to fal.ai CDN
                self.update_state(
                    state="PROCESSING",
                    meta={"step": f"uploading_image_{i+1}", "progress": progress}
                )
                import fal_client
                image_url = fal_client.upload_file(scene.reference_image_path)
            else:
                # Generate image from prompt
                self.update_state(
                    state="PROCESSING",
                    meta={"step": f"generating_image_{i+1}", "progress": progress}
                )
                try:
                    image_url = fal_service.generate_image(scene.prompt)
                    scene.generated_image_url = image_url
                    db.commit()
                except Exception as e:
                    project.status = "failed"
                    db.commit()
                    return {"status": "failed", "error": f"Image generation failed for scene {i+1}: {str(e)}"}

            # Step 2: Generate video from image
            self.update_state(
                state="PROCESSING",
                meta={"step": f"generating_video_{i+1}", "progress": progress + 10}
            )
            try:
                video_url = fal_service.generate_video_from_image(
                    image_url=image_url,
                    prompt=scene.prompt,
                    duration=5,  # 5 seconds per scene
                )
                scene.generated_video_url = video_url
                db.commit()
            except Exception as e:
                project.status = "failed"
                db.commit()
                return {"status": "failed", "error": f"Video generation failed for scene {i+1}: {str(e)}"}

            # Step 3: Download video clip
            self.update_state(
                state="PROCESSING",
                meta={"step": f"downloading_video_{i+1}", "progress": progress + 20}
            )
            clip_path = UPLOADS_PATH / "clips" / f"project_{project_id}" / f"scene_{scene.id}.mp4"
            download_file(video_url, clip_path)
            scene.video_path = str(clip_path)
            db.commit()
            video_clips.append(str(clip_path))

        # Step 4: Stitch all clips together
        self.update_state(state="PROCESSING", meta={"step": "stitching", "progress": 90})

        output_dir = UPLOADS_PATH / "output" / f"project_{project_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / "final_video.mp4")

        # Check if any scene has audio for background track
        audio_path = None
        for scene in scenes:
            if scene.audio_path:
                audio_path = scene.audio_path
                break

        try:
            video_service.stitch_videos(
                video_paths=video_clips,
                output_path=output_path,
                audio_path=audio_path,
            )
        except Exception as e:
            project.status = "failed"
            db.commit()
            return {"status": "failed", "error": f"Video stitching failed: {str(e)}"}

        # Update project with final video path
        project.output_video_path = f"output/project_{project_id}/final_video.mp4"
        project.status = "completed"
        db.commit()

        self.update_state(state="SUCCESS", meta={"step": "completed", "progress": 100})

        return {
            "status": "completed",
            "video_path": project.output_video_path,
        }

    except Exception as e:
        if project:
            project.status = "failed"
            db.commit()
        return {"status": "failed", "error": str(e)}

    finally:
        db.close()
