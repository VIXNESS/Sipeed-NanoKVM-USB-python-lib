"""
Example: AI agent loop that observes the screen and takes actions via NanoKVM.

This shows the pattern for integrating NanoKVM with an LLM-based agent.
Replace the `ask_llm()` function with your actual LLM call.
"""

from __future__ import annotations

import time

from nanokvm import NanoKVM


def ask_llm(screenshot_base64: str, instruction: str) -> dict:
    """
    Placeholder for your LLM call.
    Send the screenshot + instruction to a multimodal LLM and parse its response.

    Expected response format:
        {"action": "type", "text": "hello"}
        {"action": "key", "key": "Enter"}
        {"action": "combo", "keys": ["ctrl", "s"]}
        {"action": "click", "x": 0.5, "y": 0.5}
        {"action": "scroll", "delta": -3}
        {"action": "done"}
    """
    # Replace this with an actual API call, e.g.:
    # response = openai.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "user", "content": [
    #             {"type": "text", "text": instruction},
    #             {"type": "image_url", "image_url": {
    #                 "url": f"data:image/jpeg;base64,{screenshot_base64}"
    #             }}
    #         ]}
    #     ]
    # )
    # return json.loads(response.choices[0].message.content)

    return {"action": "done"}


def execute_action(kvm: NanoKVM, action: dict) -> None:
    """Execute a single action returned by the LLM."""
    match action["action"]:
        case "type":
            kvm.type_text(action["text"])
        case "key":
            kvm.press_key(action["key"])
        case "combo":
            kvm.key_combo(action["keys"])
        case "click":
            kvm.mouse_click(
                x=action.get("x"),
                y=action.get("y"),
                button=action.get("button", "left"),
            )
        case "scroll":
            kvm.mouse_scroll(action["delta"])
        case "move":
            kvm.mouse_move(action["x"], action["y"])
        case "done":
            pass
        case _:
            print(f"Unknown action: {action}")


def main() -> None:
    kvm = NanoKVM(serial_port="/dev/ttyACM0", video_device=0)
    kvm.connect()

    instruction = "Open the terminal and type 'ls -la', then press Enter"
    max_steps = 20

    for step in range(max_steps):
        print(f"--- Step {step + 1} ---")

        screenshot = kvm.capture_frame_base64(quality=80)
        action = ask_llm(screenshot, instruction)
        print(f"Action: {action}")

        if action["action"] == "done":
            print("Agent reports task complete.")
            break

        execute_action(kvm, action)
        time.sleep(0.5)  # wait for the action to take effect on screen

    kvm.disconnect()


if __name__ == "__main__":
    main()
