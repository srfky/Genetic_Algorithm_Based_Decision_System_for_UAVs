import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan


async def run():

    drone = System()

    await drone.connect(system_address="udp://:14540")

    print(">> Connecting to vehicle...")

    async for state in drone.core.connection_state():

        if state.is_connected:

            print(">> Vehicle connected.")

            break

    print(">> Checking GPS status...")

    async for health in drone.telemetry.health():

        if (
            health.is_global_position_ok and
            health.is_home_position_ok
        ):

            print(">> GPS is ready.")

            break

    print(">> Arming vehicle...")

    await drone.action.arm()

    print(">> Takeoff initiated...")

    await drone.action.set_takeoff_altitude(10.0)

    await drone.action.takeoff()

    print(">> Monitoring altitude...")

    timeout = 0

    max_timeout = 60  # Maximum waiting time (seconds)

    while timeout < max_timeout:

        async for position in drone.telemetry.position():

            print(
                f">> Altitude: "
                f"{position.relative_altitude_m:.2f} m"
            )

            if position.relative_altitude_m >= 5.0:

                print(">> Target altitude reached.")

                break

            await asyncio.sleep(0.5)

            timeout += 0.5

        else:
            continue

        break

    else:

        print(
            ">> Warning: Target altitude "
            "could not be reached."
        )

    # Create mission waypoints
    print(">> Creating mission plan...")

    async for position in drone.telemetry.position():

        lat = position.latitude_deg
        lon = position.longitude_deg

        break

    mission_items = [

        MissionItem(
            lat + 0.0006,
            lon,
            15.0,
            10,
            True,
            float('nan'),
            float('nan'),
            MissionItem.CameraAction.NONE,
            float('nan'),
            float('nan'),
            float('nan'),
            float('nan'),
            float('nan'),
            vehicle_action=MissionItem.VehicleAction.NONE
        ),

        MissionItem(
            lat + 0.0006,
            lon + 0.0006,
            15.0,
            10,
            True,
            float('nan'),
            float('nan'),
            MissionItem.CameraAction.NONE,
            float('nan'),
            float('nan'),
            float('nan'),
            float('nan'),
            float('nan'),
            vehicle_action=MissionItem.VehicleAction.LAND
        )
    ]

    mission_plan = MissionPlan(mission_items)

    await drone.mission.set_return_to_launch_after_mission(False)

    await drone.mission.upload_mission(mission_plan)

    print(">> Starting mission...")

    await drone.mission.start_mission()

    # Switch to fixed-wing mode during mission
    print(">> Switching to fixed-wing mode...")

    try:

        await drone.action.transition_to_fixedwing()

        await asyncio.sleep(5)

        print(">> Fixed-wing mode activated.")

    except Exception as e:

        print(f">> Fixed-wing transition failed: {e}")

    async for mission_progress in drone.mission.mission_progress():

        print(
            f">> Mission Progress: "
            f"{mission_progress.current}/"
            f"{mission_progress.total}"
        )

        if mission_progress.current == mission_progress.total:

            print(">> All mission waypoints completed.")

            break

        await asyncio.sleep(1)

    print(">> Returning to launch...")

    await drone.action.return_to_launch()

    async for in_air in drone.telemetry.in_air():

        if not in_air:

            print(">> Vehicle landed.")

            break

        await asyncio.sleep(1)

    print(">> Mission completed successfully.")


if __name__ == "__main__":

    asyncio.run(run())