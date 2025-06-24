export function Table({ children }) {
  return <table className="min-w-full border">{children}</table>;
}
export function TableHead({ children }) {
  return <thead className="bg-gray-100">{children}</thead>;
}
export function TableRow({ children }) {
  return <tr className="border-b">{children}</tr>;
}
export function TableHeader({ children }) {
  return <th className="px-2 py-1 text-left">{children}</th>;
}
export function TableBody({ children }) {
  return <tbody>{children}</tbody>;
}
export function TableCell({ children }) {
  return <td className="px-2 py-1">{children}</td>;
}
