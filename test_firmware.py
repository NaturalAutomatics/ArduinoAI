from firmware_manager import FirmwareManager

# Test firmware generation
fm = FirmwareManager()

# Test with basic sensors
sensors = ["temperature", "light"]
logic = "// Basic monitoring"

sketch = fm.create_firmware(sensors, logic)
print("Generated Arduino sketch:")
print("=" * 50)
print(sketch)
print("=" * 50)

# Save and check
metadata = {"test": True}
sketch_path = fm.save_firmware_version(sketch, metadata)
print(f"Saved to: {sketch_path}")