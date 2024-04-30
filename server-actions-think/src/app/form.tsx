"use client";

import { createTodo } from "./action";
import { useCustomActionState } from "./hook";
import { Dialog, useDialog } from "./dialog";

export const Form = () => {
  const { ref, open } = useDialog();
  const { state, action, isPending } = useCustomActionState(
    createTodo,
    { value: null, error: null },
    (state) => {
      console.log("error", state);
      open();
    },
    (state) => {
      console.log("success", state);
    }
  );
  return (
    <form action={action}>
      <div className="flex flex-col items-center justify-center space-y-4">
        <h1 className="text-4xl font-bold">Sample Form</h1>
        <p className="text-lg text-center">Think is a simple form</p>
        <div className="flex flex-col items-center justify-center space-y-4">
          <input
            type="text"
            placeholder="What are you thinking about?"
            className="p-4 border border-gray-300 rounded-lg"
          />
          <button
            disabled={isPending}
            className="p-4 bg-blue-500 text-white rounded-lg"
          >
            Submit
          </button>
        </div>
      </div>
      <Dialog ref={ref} />
    </form>
  );
};
