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
    channel_3 = Channel(
        mode=Modes.DOUBLET,
        no_channel=3,
        amplitude=20,
        pulse_width=35,
        name="Triceps",
        frequency=25,
        ramp=5,
        device_type=Device.Rehastimp24,
    )
    channel_4 = Channel(
        mode=Modes.TRIPLET,
        no_channel=4,
        amplitude=40,
        pulse_width=500,
        name="Quadriceps",
        frequency=15,
        ramp=1,
        device_type=Device.Rehastimp24,
    )
    list_channels = [channel_2]

    # --- Initialize stimulator ---
    stimulator = St(port="COM4", show_log="Status")

    print("[Mid-level] Initializing stimulation...")
    stimulator.init_stimulation(list_channels=list_channels)

    print("[Mid-level] Starting async stimulation for 5 seconds...")
    # Create tasks so both stimulation and ticker run concurrently.
    stimulation_task = asyncio.create_task(
        stimulator.start_stimulation_async(
            upd_list_channels=list_channels,
            stimulation_duration=5,
            safety=True,
        )
    )
    ticker_task = asyncio.create_task(ticker(5, label="Stimulation"))

    # Wait for both tasks to finish.
    await asyncio.gather(stimulation_task, ticker_task)
    print("[Mid-level] Async stimulation complete.")

    # Update channel parameters mid-stimulation
    print("[Mid-level] Updating channel 2 parameters...")
    channel_2.set_amplitude(15)
    channel_2.set_pulse_width(200)
    channel_2.set_frequency(10)
    channel_2.set_mode(Modes.TRIPLET)

    print("[Mid-level] Restarting async stimulation for another 5 seconds...")
    stimulation_update_task = asyncio.create_task(
        stimulator.update_stimulation_async(
            upd_list_channels=list_channels,
            stimulation_duration=5,
        )
    )
    ticker_update_task = asyncio.create_task(ticker(5, label="Update Stimulation"))

    await asyncio.gather(stimulation_update_task, ticker_update_task)
    print("[Mid-level] Async update stimulation complete.")

    print("[Mid-level] Ending stimulation...")
    stimulator.end_stimulation()

    # --- Low-level stimulation example (kept commented) ---
    '''
    print("[Low-level] Starting low-level stimulation...")
    stimulator.start_stim_one_channel_stimulation(
        no_channel=1,
        points=points,
        stim_sequence=30,
        pulse_interval=10,
    )
    print("[Low-level] Low-level stimulation complete.")

    # Update low-level points
    print("[Low-level] Updating stimulation points...")
    points[0].set_amplitude(30); points[0].set_pulse_width(350)
    points[1].set_amplitude(-30); points[1].set_pulse_width(350)
    points[2].set_amplitude(20); points[2].set_pulse_width(350)
    points[3].set_amplitude(-20); points[3].set_pulse_width(350)

    stimulator.update_stim_one_channel(upd_list_point=points)
    print("[Low-level] Low-level update complete.")

    print("[Low-level] Stopping low-level stimulation...")
    stimulator.end_stim_one_channel()
    '''
    print("Closing connection to RehastimP24...")
    stimulator.close_port()

if __name__ == "__main__":
    asyncio.run(main())
