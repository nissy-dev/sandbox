export type LinkProps = {
  /**
   * リンクの property 1
   */
  prop1: string;
  /**
   * リンクの property 2
   */
  prop2?: string;
};

export const Button = ({ prop1, prop2 }: LinkProps) => {
  return <button>{prop1}</button>;
};
