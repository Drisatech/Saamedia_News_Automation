#!/usr/bin/env python3
"""
Debug script to find the correct import path for wordpress xmlrpc
"""

import os
import sys
import pkgutil

def check_wordpress_modules():
    """Check for wordpress-related modules"""
    print("=== Checking for WordPress modules ===")
    
    # Method 1: Check all importable modules
    print("\n1. Checking importable modules:")
    for importer, modname, ispkg in pkgutil.iter_modules():
        if 'wordpress' in modname.lower() or 'xmlrpc' in modname.lower():
            print(f"   Found module: {modname} (package: {ispkg})")
    
    # Method 2: Check site-packages directory
    print("\n2. Checking site-packages directory:")
    site_packages = None
    for path in sys.path:
        if 'site-packages' in path:
            site_packages = path
            break
    
    if site_packages and os.path.exists(site_packages):
        print(f"   Site-packages: {site_packages}")
        for item in os.listdir(site_packages):
            if 'wordpress' in item.lower():
                print(f"   Found package directory: {item}")
                
                # Check subdirectories
                item_path = os.path.join(site_packages, item)
                if os.path.isdir(item_path):
                    print(f"   Contents of {item}:")
                    try:
                        for subitem in os.listdir(item_path):
                            if not subitem.startswith('.'):
                                print(f"     - {subitem}")
                    except PermissionError:
                        print("     (Permission denied)")
    
    # Method 3: Try different import variations
    print("\n3. Testing import variations:")
    import_attempts = [
        "wordpress_xmlrpc",
        "python_wordpress_xmlrpc", 
        "wordpressxmlrpc",
        "wordpress.xmlrpc"
    ]
    
    for attempt in import_attempts:
        try:
            __import__(attempt)
            print(f"   ✓ SUCCESS: {attempt}")
            
            # Try to import Client
            try:
                module = __import__(attempt, fromlist=['Client'])
                if hasattr(module, 'Client'):
                    print(f"     - Client class available")
                else:
                    print(f"     - Client class NOT found")
            except Exception as e:
                print(f"     - Error importing Client: {e}")
                
        except ImportError as e:
            print(f"   ✗ FAILED: {attempt} - {e}")
    
    # Method 4: Try methods import
    print("\n4. Testing methods import:")
    for base in ["wordpress_xmlrpc", "python_wordpress_xmlrpc"]:
        try:
            methods_module = f"{base}.methods.posts"
            __import__(methods_module)
            print(f"   ✓ SUCCESS: {methods_module}")
        except ImportError as e:
            print(f"   ✗ FAILED: {methods_module} - {e}")

if __name__ == "__main__":
    check_wordpress_modules()
    
    print("\n=== Recommendation ===")
    print("Based on the results above, use the import statement that shows '✓ SUCCESS'")
    print("If none work, the package might not be installed correctly.")