import fal_client


class FalService:
    """Service for interacting with fal.ai API for image and video generation."""

    # Model options - cheap vs quality
    IMAGE_MODELS = {
        "schnell": "fal-ai/flux/schnell",  # $0.003/MP - fast, cheap
        "dev": "fal-ai/flux/dev",           # ~$0.05 - better quality
    }

    VIDEO_MODELS = {
        "ovi": "fal-ai/ovi/image-to-video",                      # $0.20/video - cheap
        "kling": "fal-ai/kling-video/v1/standard/image-to-video", # ~$0.50 - better quality
    }

    def __init__(self, quality: str = "cheap"):
        """
        Initialize FalService.

        Args:
            quality: "cheap" for budget models, "quality" for better results
        """
        if quality == "cheap":
            self.image_model = self.IMAGE_MODELS["schnell"]
            self.video_model = self.VIDEO_MODELS["ovi"]
        else:
            self.image_model = self.IMAGE_MODELS["dev"]
            self.video_model = self.VIDEO_MODELS["kling"]

    def generate_image(self, prompt: str, image_size: str = "landscape_16_9") -> str:
        """
        Generate an image from a text prompt.
        Returns the URL of the generated image.
        """
        result = fal_client.run(
            self.image_model,
            arguments={
                "prompt": prompt,
                "image_size": image_size,
                "num_images": 1,
            },
        )
        return result["images"][0]["url"]

    def generate_video_from_image(
        self, image_url: str, prompt: str = "", duration: int = 5
    ) -> str:
        """
        Generate a video clip from an image.
        Returns the URL of the generated video.
        """
        args = {
            "prompt": prompt,
            "image_url": image_url,
        }

        # Kling supports duration, Ovi doesn't
        if "kling" in self.video_model:
            args["duration"] = duration

        result = fal_client.run(self.video_model, arguments=args)
        return result["video"]["url"]

    async def generate_image_async(self, prompt: str, image_size: str = "landscape_16_9") -> str:
        """Async version of generate_image."""
        result = await fal_client.run_async(
            self.image_model,
            arguments={
                "prompt": prompt,
                "image_size": image_size,
                "num_images": 1,
            },
        )
        return result["images"][0]["url"]

    async def generate_video_from_image_async(
        self, image_url: str, prompt: str = "", duration: int = 5
    ) -> str:
        """Async version of generate_video_from_image."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
        }

        if "kling" in self.video_model:
            args["duration"] = duration

        result = await fal_client.run_async(self.video_model, arguments=args)
        return result["video"]["url"]
