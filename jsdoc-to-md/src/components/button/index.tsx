export type ButtonProps = {
  /**
   * ボタンの property 1
   */
  prop1: string;
  /**
   * ボタンの property 2
   */
  prop2: string;
};

export const Button = ({ prop1, prop2 }: ButtonProps) => {
  return <button>{prop1}</button>;
};
