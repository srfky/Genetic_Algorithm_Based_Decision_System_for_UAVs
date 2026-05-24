import RPi.GPIO as GPIO
from time import sleep

# Motor pin configuration (BCM numbering)
motor_pins = [
    (24, 23, 18),  # M1 - Front Left
    (17, 27, 22),  # M2 - Front Right
    (5, 6, 13),    # M3 - Rear Left
    (19, 26, 12)   # M4 - Rear Right
]

# GPIO setup
GPIO.setmode(GPIO.BCM)

pwm_list = []
gpio_initialized = False


try:
    # Initialize motor pins and PWM signals
    for in1, in2, en in motor_pins:

        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)
        GPIO.setup(en, GPIO.OUT)

        pwm = GPIO.PWM(en, 1000)
        pwm.start(0)

        pwm_list.append(pwm)

    gpio_initialized = True

except Exception as e:

    print(f"Error while initializing GPIO: {e}")

    if GPIO.getmode() is not None:
        GPIO.cleanup()

    exit()


def run_motor(motor_no, direction, speed):
    """
    Control a single motor direction and speed.
    """

    if not gpio_initialized:
        return

    in1, in2, _ = motor_pins[motor_no]
    pwm = pwm_list[motor_no]

    if direction == 'forward':

        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)

    elif direction == 'backward':

        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)

    elif direction == 'stop':

        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)

    try:
        pwm.ChangeDutyCycle(speed)

    except Exception as e:
        print(f"PWM error on motor {motor_no}: {e}")


# -----------------------------
# Robot movement functions
# -----------------------------

def move_forward(speed=50, wait_time=0.5):
    """
    Move the robot forward.
    """

    for i in range(4):
        run_motor(i, 'forward', speed)

    sleep(wait_time)

    stop_robot()


def move_backward(speed=50, wait_time=0.5):
    """
    Move the robot backward.
    """

    for i in range(4):
        run_motor(i, 'backward', speed)

    sleep(wait_time)

    stop_robot()


def stop_robot():
    """
    Stop all motors.
    """

    for i in range(4):
        run_motor(i, 'stop', 0)

    sleep(0.1)


def turn_right(speed=50, wait_time=0.5):
    """
    Turn the robot right.
    """

    run_motor(0, 'forward', speed)
    run_motor(2, 'forward', speed)

    run_motor(1, 'backward', speed)
    run_motor(3, 'backward', speed)

    sleep(wait_time)

    stop_robot()


def turn_left(speed=50, wait_time=0.5):
    """
    Turn the robot left.
    """

    run_motor(0, 'backward', speed)
    run_motor(2, 'backward', speed)

    run_motor(1, 'forward', speed)
    run_motor(3, 'forward', speed)

    sleep(wait_time)

    stop_robot()


# -----------------------------
# Direction definitions
# -----------------------------

directions = {
    (0, 1): "East",
    (0, -1): "West",
    (1, 0): "South",
    (-1, 0): "North"
}


turns = {
    ("North", "East"): "Turn Right",
    ("North", "West"): "Turn Left",

    ("South", "East"): "Turn Left",
    ("South", "West"): "Turn Right",

    ("East", "South"): "Turn Right",
    ("East", "North"): "Turn Left",

    ("West", "South"): "Turn Left",
    ("West", "North"): "Turn Right"
}


def read_path_from_file(filename="received_data.txt"):
    """
    Read robot path coordinates from file.
    """

    path = []

    try:
        with open(filename, 'r') as file:

            for line in file:

                clean_line = (
                    line.strip()
                    .replace('(', '')
                    .replace(')', '')
                )

                coords = tuple(map(int, clean_line.split(',')))

                path.append(coords)

        return path

    except FileNotFoundError:

        print(f"Error: '{filename}' file not found.")

        return None

    except Exception as e:

        print(f"Error while reading file: {e}")

        return None


def follow_path_and_drive(
        path,
        speed=50,
        forward_wait=0.5,
        turn_wait=1.0):
    """
    Follow the given coordinate path
    and control robot movements.
    """

    if not path or len(path) < 2:

        print("Invalid path. Robot cannot move.")

        return

    previous_direction = None

    for i in range(len(path) - 1):

        start = path[i]
        target = path[i + 1]

        movement = (
            target[0] - start[0],
            target[1] - start[1]
        )

        current_direction = directions.get(movement)

        if not current_direction:

            print(f"Invalid movement detected: {movement}")

            continue

        # Initial movement
        if previous_direction is None:

            print(f"{start} -> {target} | Direction: {current_direction}")

            move_forward(speed, forward_wait)

        # Continue in same direction
        elif previous_direction == current_direction:

            print(f"{start} -> {target} | Moving Forward")

            move_forward(speed, forward_wait)

        # Change direction
        else:

            turn = turns.get(
                (previous_direction, current_direction),
                "Unknown Turn"
            )

            print(f"{start} -> {target} | {turn}")

            if turn == "Turn Right":

                turn_right(speed, turn_wait)

            elif turn == "Turn Left":

                turn_left(speed, turn_wait)

            else:

                move_forward(speed, forward_wait)

        previous_direction = current_direction

    print("\nPath completed.")

    stop_robot()


# -----------------------------
# Main Program
# -----------------------------

if __name__ == "__main__":

    robot_path = read_path_from_file("received_data.txt")

    if robot_path:

        try:

            print("Robot started following the path...")

            follow_path_and_drive(
                robot_path,
                speed=60,
                forward_wait=0.7,
                turn_wait=1.2
            )

        except KeyboardInterrupt:

            print("\nProgram interrupted by user.")

        except Exception as e:

            print(f"Unexpected runtime error: {e}")

        finally:

            # Stop all PWM objects
            if gpio_initialized:

                for pwm_obj in pwm_list:

                    try:
                        pwm_obj.stop()

                    except Exception as e:
                        print(f"Error stopping PWM: {e}")

                # Cleanup GPIO
                try:

                    if GPIO.getmode() is not None:

                        GPIO.cleanup()

                        print("GPIO cleaned successfully.")

                except Exception as e:

                    print(f"GPIO cleanup error: {e}")

            print("Program terminated.")

    else:

        print("Path data could not be loaded.")