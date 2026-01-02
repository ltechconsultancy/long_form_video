import fal_client


class FalService:
    """Service for interacting with fal.ai API for image and video generation."""

    def generate_image(self, prompt: str, image_size: str = "landscape_16_9") -> str:
        """
        Generate an image from a text prompt.
        Returns the URL of the generated image.
        """
        result = fal_client.run(
            "fal-ai/flux/dev",
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

        Args:
            image_url: URL of the source image
            prompt: Motion/action prompt for the video
            duration: Video length in seconds (5 or 10)
        """
        result = fal_client.run(
            "fal-ai/kling-video/v1/standard/image-to-video",
            arguments={
                "prompt": prompt,
                "image_url": image_url,
                "duration": duration,
            },
        )
        return result["video"]["url"]

    async def generate_image_async(self, prompt: str, image_size: str = "landscape_16_9") -> str:
        """Async version of generate_image."""
        result = await fal_client.run_async(
            "fal-ai/flux/dev",
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
        result = await fal_client.run_async(
            "fal-ai/kling-video/v1/standard/image-to-video",
            arguments={
                "prompt": prompt,
                "image_url": image_url,
                "duration": duration,
            },
        )
        return result["video"]["url"]
