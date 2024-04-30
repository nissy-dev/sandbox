import { useActionState, useEffect } from "react";

type State<T> = {
  value: T | null;
  error: Error | null;
};

function serverActonError(e: unknown) {
  return new Error("Server action failed");
}

export const useCustomActionState = <T>(
  serverAction: () => Promise<T>,
  initialState: State<T>,
  onError?: (state: State<T>) => void,
  onSuccess?: (state: State<T>) => void
) => {
  const [state, action, isPending] = useActionState(async () => {
    try {
      const data = await serverAction();
      return { value: data, error: null };
    } catch (e) {
      return { value: null, error: serverActonError(e) };
    }
  }, initialState);

  useEffect(() => {
    if (state.error !== null && onError !== undefined) {
      onError(state);
    }

    if (state.value !== null && onSuccess !== undefined) {
      onSuccess(state);
    }
  }, [state.value, state.error]);

  return {
    state,
    action,
    isPending,
  };
};
