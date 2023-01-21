import useSWR from "swr";

const fetcher = async () => {
  const res = await fetch("/api/hello");
  return res.json();
};

const getGlobalData = () => {
  // @ts-ignore
  return __globalData__;
};

export function App() {
  const { data } = useSWR("/api/hello", fetcher);
  const globalData = getGlobalData();
  return (
    <div>
      <div>Hello World!</div>
      <div>Global data : {globalData}</div>
      <div>Fetch data : {data}</div>
    </div>
  );
}
