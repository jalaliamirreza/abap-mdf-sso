#!/usr/bin/env python3
"""
Create ZIP archive from SAP payroll export files.
This script reads the 4 payroll files and creates a ZIP archive.

Usage:
    python create_payroll_zip.py <directory_path> [output_zip_name]

Example:
    python create_payroll_zip.py /usr/sap/tmp/payroll_files payroll_export.zip
"""

import os
import sys
import zipfile
from pathlib import Path


def create_payroll_zip(directory_path, output_zip_name=None):
    """
    Create ZIP archive from payroll files in the specified directory.

    Args:
        directory_path: Path to directory containing the payroll files
        output_zip_name: Optional name for output ZIP file (default: payroll_export.zip)

    Returns:
        Path to created ZIP file
    """
    directory = Path(directory_path)

    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory_path}")

    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")

    # Define the required files
    required_files = [
        'DSKKAR00.XLS',
        'DSKWOR00.XLS',
        'DSKKAR00.DBF',
        'DSKWOR00.DBF'
    ]

    # Check which files exist
    existing_files = []
    missing_files = []

    for filename in required_files:
        file_path = directory / filename
        if file_path.exists():
            existing_files.append(file_path)
            # Print file size for verification
            file_size = file_path.stat().st_size
            print(f"Found: {filename} ({file_size} bytes)")
        else:
            missing_files.append(filename)

    if not existing_files:
        raise ValueError("No payroll files found in directory")

    if missing_files:
        print(f"Warning: Missing files: {', '.join(missing_files)}")

    # Determine output ZIP file name
    if output_zip_name is None:
        output_zip_name = 'payroll_export.zip'

    # Ensure .zip extension
    if not output_zip_name.endswith('.zip'):
        output_zip_name += '.zip'

    # Create ZIP file in the same directory
    zip_path = directory / output_zip_name

    print(f"\nCreating ZIP archive: {zip_path}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in existing_files:
            # Add file to ZIP with just the filename (no path)
            arcname = file_path.name
            zipf.write(file_path, arcname=arcname)

            # Verify the file was added correctly
            zip_info = zipf.getinfo(arcname)
            print(f"Added to ZIP: {arcname} ({zip_info.file_size} bytes uncompressed, {zip_info.compress_size} bytes compressed)")

    # Verify ZIP file was created
    if zip_path.exists():
        zip_size = zip_path.stat().st_size
        print(f"\nZIP file created successfully: {zip_path}")
        print(f"ZIP file size: {zip_size} bytes")

        # Verify ZIP integrity
        print("\nVerifying ZIP integrity...")
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Test ZIP file integrity
            bad_file = zipf.testzip()
            if bad_file is not None:
                print(f"WARNING: Corrupt file in ZIP: {bad_file}")
            else:
                print("ZIP integrity check passed ✓")

            # List contents
            print("\nZIP contents:")
            for info in zipf.infolist():
                print(f"  - {info.filename}: {info.file_size} bytes")

        return str(zip_path)
    else:
        raise RuntimeError("ZIP file was not created")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python create_payroll_zip.py <directory_path> [output_zip_name]")
        print("\nExample:")
        print("  python create_payroll_zip.py /usr/sap/tmp/payroll_files")
        print("  python create_payroll_zip.py /usr/sap/tmp/payroll_files custom_name.zip")
        sys.exit(1)

    directory_path = sys.argv[1]
    output_zip_name = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        zip_path = create_payroll_zip(directory_path, output_zip_name)
        print(f"\n✓ Success! ZIP file created at: {zip_path}")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
