from typing import Optional

# TODO: Temporary image storage (will need to be replaced with API calls - /images later)

TEMPORARY_UBUNTU_IMAGES = {
    "ubuntu 24.04 lts (cloud)": "2fd07c5d-3104-4931-882b-4fe6a115c3bd",
    "ubuntu 22.04 lts (jammy jellyfish) (cloud)": "c2e5b7be-32ea-4f74-bb88-1c9a4104f8ca",
    "ubuntu 20.04 lts (focal fossa) (cloud)": "f0927f2c-7b84-4bc9-ac8c-a0891ffb16d4"
}

def find_os_image_uuid_by_name(image_name: str) -> Optional[str]:
    """
    Find image ID by name (case-insensitive match).
    
    Args:
        image_name: The name of the image to search for (e.g., "Ubuntu 22.04")
    
    Returns:
        str: Image UUID if found, None otherwise
    """
    for os_img_name, os_img_uuid in TEMPORARY_UBUNTU_IMAGES.items():
        if os_img_name == image_name.lower():
            return os_img_uuid
        
    # Default to Ubuntu 20.04 if no match found
    return TEMPORARY_UBUNTU_IMAGES["ubuntu 20.04 lts (focal fossa) (cloud)"]