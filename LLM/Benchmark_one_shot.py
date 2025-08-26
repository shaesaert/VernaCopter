from examples.one_shot_automatic import run_one_shot
import traceback


def run_multiple_times(n=20, scenario="treasure_hunt"):
    success_count = 0
    results = []
    specs = []

    for i in range(1, n + 1):
        print(f"\n=== Run {i} ===")
        try:
            messages, task_accomplished, waypoints, spec= run_one_shot(scenario)
            specs.append(spec)
            results.append(task_accomplished)
            if task_accomplished:
                print(f"Run {i}: ✅ Task accomplished")
                success_count += 1
            else:
                print(f"Run {i}: ❌ Task failed")

        except Exception as e:
            print(f"Run {i}: ⚠️ Error occurred")
            traceback.print_exc()
            results.append(False)

    print("\n=== Summary ===")
    print(f"Total successes: {success_count}/{n}")
    return results


if __name__ == "__main__":
    run_multiple_times(30)