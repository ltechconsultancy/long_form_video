import fal_client


# Available models for selection
IMAGE_MODELS = {
    "fal-ai/flux/schnell": {"name": "Flux Schnell", "price": "$0.003/MP", "speed": "Fast"},
    "fal-ai/flux/dev": {"name": "Flux Dev", "price": "$0.05/MP", "speed": "Medium"},
    "fal-ai/fast-sdxl": {"name": "SDXL Fast", "price": "$0.01/MP", "speed": "Fast"},
}

VIDEO_MODELS = {
    "fal-ai/ovi/image-to-video": {"name": "Ovi", "price": "$0.20", "speed": "Fast", "duration_support": False},
    "fal-ai/kling-video/v1/standard/image-to-video": {"name": "Kling 1.0", "price": "$0.50", "speed": "Medium", "duration_support": True},
    "fal-ai/kling-video/v1.5/pro/image-to-video": {"name": "Kling 1.5 Pro", "price": "$0.80", "speed": "Slow", "duration_support": True},
    "fal-ai/minimax-video/image-to-video": {"name": "MiniMax", "price": "$0.35", "speed": "Medium", "duration_support": False},
}

IMAGE_SIZES = {
    "square": "1:1 Square",
    "square_hd": "1:1 Square HD",
    "portrait_4_3": "4:3 Portrait",
    "portrait_16_9": "16:9 Portrait",
    "landscape_4_3": "4:3 Landscape",
    "landscape_16_9": "16:9 Landscape",
}


class FalService:
    """Service for interacting with fal.ai API for image and video generation."""

    def __init__(
        self,
        image_model: str = "fal-ai/flux/schnell",
        video_model: str = "fal-ai/ovi/image-to-video",
    ):
        self.image_model = image_model
        self.video_model = video_model

    def generate_image(self, prompt: str, image_size: str = "landscape_16_9") -> str:
        """Generate an image from a text prompt."""
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
        """Generate a video clip from an image."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
        }

        # Only add duration for models that support it
        model_info = VIDEO_MODELS.get(self.video_model, {})
        if model_info.get("duration_support", False):
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

        model_info = VIDEO_MODELS.get(self.video_model, {})
        if model_info.get("duration_support", False):
            args["duration"] = duration

        result = await fal_client.run_async(self.video_model, arguments=args)
        return result["video"]["url"]
