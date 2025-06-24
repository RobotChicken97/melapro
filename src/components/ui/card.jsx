export function Card({ children }) {
  return <div className="border rounded p-4 bg-white">{children}</div>;
}
export function CardHeader({ children }) {
  return <div className="mb-2 font-semibold">{children}</div>;
}
export function CardTitle({ children }) {
  return <h3 className="text-lg font-bold">{children}</h3>;
}
export function CardDescription({ children }) {
  return <p className="text-sm text-gray-500">{children}</p>;
}
export function CardContent({ children }) {
  return <div className="mt-2">{children}</div>;
}
