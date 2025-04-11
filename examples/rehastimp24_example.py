import asyncio
import time
from pysciencemode import Channel, Point, Device, Modes
from pysciencemode import RehastimP24 as St

# A simple async ticker that prints every second for a specified duration.
async def ticker(duration, label="Ticker"):
    start_time = time.time()
    while time.time() - start_time < duration:
        print(f"[{label}] Tick at {time.strftime('%X')}")
        await asyncio.sleep(1)  # Non-blocking sleep

async def main():
    # --- Setup channels for mid-level stimulation ---
    # (We only use one channel here to focus on cancellation/update behavior.)
    channel_1 = Channel(
        no_channel=1,
        name="Biceps",
        frequency=20,
        device_type=Device.Rehastimp24,
        amplitude=25,
        pulse_width=100,
    )
    channel_2 = Channel(
        mode=Modes.SINGLE,
        no_channel=1,
        amplitude=25,
        pulse_width=100,
        name="Calf",
        frequency=50,
        ramp=16,
        device_type=Device.Rehastimp24,
    )
    # For the purpose of this example we use a list containing channel_2 only.
    list_channels = [channel_2]

    # --- Initialize stimulator ---
    stimulator = St(port="COM4", show_log="Status")
    print(f"[{time.strftime('%X')}] [Mid-level] Initializing stimulation...")
    stimulator.init_stimulation(list_channels=list_channels)

    # --- Start an initial stimulation task with a long duration (10 seconds) ---
    print(f"[{time.strftime('%X')}] [Mid-level] Starting initial async stimulation for 10 seconds...")
    initial_stimulation_task = asyncio.create_task(
        stimulator.start_stimulator_async(
            upd_list_channels=list_channels,
            stimulation_duration=10,
            safety=True,
        )
    )

    # Start a ticker that runs for 12 seconds.
    ticker_task = asyncio.create_task(ticker(12, label="Stimulation Ticker"))

    # Let the initial stimulation run for 3 seconds before issuing an update.
    await asyncio.sleep(3)
    print(f"[{time.strftime('%X')}] [Mid-level] Requesting stimulation update before initial stimulation elapses...")

    # --- Change channel parameters mid-run ---
    channel_2.set_amplitude(15)
    channel_2.set_pulse_width(200)
    channel_2.set_frequency(10)
    channel_2.set_mode(Modes.TRIPLET)

    # Call the update_stimulation_async function.
    # This should cancel the previous stimulation task (if still running) and start a new one.
    update_stimulation_task = asyncio.create_task(
        stimulator.update_stimulation_async(
            upd_list_channels=list_channels,
            stimulation_duration=8,  # New duration (could be different from the original)
        )
    )
    print(f"[{time.strftime('%X')}] [Mid-level] Update stimulation task initiated.")

    # Wait for both the (cancellation/updated) stimulation and the ticker to finish.
    # Because update_stimulation_async cancels the previous task if it's still running,
    # you should see evidence of cancellation in the log prints.
    await asyncio.gather(initial_stimulation_task, update_stimulation_task, ticker_task)
    print(f"[{time.strftime('%X')}] [Mid-level] Async stimulation update complete.")

    print(f"[{time.strftime('%X')}] [Mid-level] Ending stimulation...")
    stimulator.end_stimulation()

    print(f"[{time.strftime('%X')}] Closing connection to RehastimP24...")
    stimulator.close_port()

if __name__ == "__main__":
    asyncio.run(main())
