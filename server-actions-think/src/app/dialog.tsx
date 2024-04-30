import { forwardRef, useCallback, useRef } from "react";

export function useDialog() {
  const ref = useRef<HTMLDialogElement | null>(null);

  const open = useCallback(() => {
    if (ref.current === null) {
      return;
    }
    ref.current?.showModal();
  }, [ref]);
  return { ref, open };
}

export const Dialog = forwardRef<HTMLDialogElement, {}>((_, ref) => {
  return (
    <dialog ref={ref} className="fixed inset-0 z-10 overflow-y-auto">
      <div className="flex items-center justify-center">
        <div className="bg-white rounded-lg p-8 z-20">
          <div className="text-xl font-semibold mb-4">エラーが発生</div>
        </div>
      </div>
      <div className="fixed inset-0 bg-black opacity-50"></div>
    </dialog>
  );
});

Dialog.displayName = "Dialog";
