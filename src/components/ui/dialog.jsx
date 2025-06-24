export function Dialog({ children }) {
  return <div className="fixed inset-0 flex items-center justify-center bg-black/50">{children}</div>;
}
export function DialogContent({ children }) {
  return <div className="bg-white p-4 rounded shadow">{children}</div>;
}
export function DialogHeader({ children }) {
  return <div className="font-bold mb-2">{children}</div>;
}
export function DialogFooter({ children }) {
  return <div className="mt-2">{children}</div>;
}
export function DialogTitle({ children }) {
  return <h3 className="text-lg font-semibold">{children}</h3>;
}
export function DialogDescription({ children }) {
  return <p className="text-sm text-gray-600">{children}</p>;
}
