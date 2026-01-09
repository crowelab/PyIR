import sys
import os
from pathlib import Path

if sys.version_info >= (3, 9):
    from importlib import resources
    HAS_IMPORTLIB_RESOURCES = True
else:
    try:
        import importlib_resources as resources
        HAS_IMPORTLIB_RESOURCES = True
    except ImportError:
        HAS_IMPORTLIB_RESOURCES = False


def get_resource_path(package_name: str, resource_path: str) -> str:
    """
    Get the absolute path to a resource file within a package.
    
    Args:
        package_name: Name of the package (e.g., 'crowelab_pyir')
        resource_path: Path to the resource relative to package root (e.g., 'data/germlines')
    
    Returns:
        Absolute path to the resource as a string
    
    Raises:
        FileNotFoundError: If the resource doesn't exist
        ModuleNotFoundError: If the package doesn't exist
    """
    if HAS_IMPORTLIB_RESOURCES:
        try:
            # Split the resource path to get the subpackage and filename
            path_parts = resource_path.split('/')
            
            # For Python 3.9+, use the modern files() API
            if sys.version_info >= (3, 9):
                # Build the full package path
                full_package = package_name
                if len(path_parts) > 1:
                    full_package = f"{package_name}.{'.'.join(path_parts[:-1])}"
                    filename = path_parts[-1]
                else:
                    filename = path_parts[0]
                
                package_files = resources.files(full_package)
                if filename:
                    resource_path_obj = package_files / filename
                else:
                    resource_path_obj = package_files
                
                return str(resource_path_obj)
            
            else:
                # For Python 3.6-3.8 with importlib_resources backport
                # Use the as_file() context manager for directories or files()
                if len(path_parts) > 1:
                    # For nested paths, we need to traverse
                    package_parts = path_parts[:-1]
                    filename = path_parts[-1]
                    full_package = f"{package_name}.{'.'.join(package_parts)}"
                    
                    try:
                        # Try using files() if available (newer versions of backport)
                        if hasattr(resources, 'files'):
                            package_files = resources.files(full_package)
                            resource_path_obj = package_files / filename
                            return str(resource_path_obj)
                        else:
                            # Fallback to path() context manager
                            with resources.path(full_package, filename) as resource_path_obj:
                                return str(resource_path_obj)
                    except (TypeError, AttributeError):
                        # If that doesn't work, try the old way
                        with resources.path(full_package, filename) as resource_path_obj:
                            return str(resource_path_obj)
                else:
                    # Single component path
                    filename = path_parts[0]
                    if hasattr(resources, 'files'):
                        package_files = resources.files(package_name)
                        if filename:
                            resource_path_obj = package_files / filename
                        else:
                            resource_path_obj = package_files
                        return str(resource_path_obj)
                    else:
                        with resources.path(package_name, filename) as resource_path_obj:
                            return str(resource_path_obj)
                
        except (ModuleNotFoundError, FileNotFoundError, AttributeError, TypeError) as e:
            # If importlib_resources fails, fall back to manual path resolution
            pass
    
    # Fallback: try to find the resource relative to the package location
    try:
        import crowelab_pyir
        package_dir = Path(crowelab_pyir.__file__).parent
        resource_full_path = package_dir / resource_path
        if resource_full_path.exists():
            return str(resource_full_path)
    except:
        pass
    
    # Last resort: try relative to current working directory
    try:
        # Look for the package in common locations
        possible_paths = [
            Path('./pyir') / resource_path,  # Development mode
            Path('./crowelab_pyir') / resource_path,  # Installed mode
            Path(os.path.dirname(__file__)) / resource_path,  # Relative to this file
        ]
        
        for possible_path in possible_paths:
            if possible_path.exists():
                return str(possible_path.resolve())
    except:
        pass
        
    raise FileNotFoundError(f"Resource '{resource_path}' not found in package '{package_name}'")


def get_data_path(subpath: str = '') -> str:
    """
    Convenience function to get paths within the crowelab_pyir/data directory.
    
    Args:
        subpath: Path relative to the data directory (e.g., 'germlines', 'bin')
    
    Returns:
        Absolute path to the data resource
    """
    if subpath:
        return get_resource_path('crowelab_pyir', f'data/{subpath}')
    else:
        return get_resource_path('crowelab_pyir', 'data')