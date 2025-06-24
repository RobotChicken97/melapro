import { useState, useRef } from 'react';

export function DropdownMenu({ children }) {
  return <div className="relative inline-block">{children}</div>;
}
export function DropdownMenuTrigger({ children }) {
  return <div>{children}</div>;
}
export function DropdownMenuContent({ children }) {
  return (
    <div className="absolute right-0 mt-2 w-48 bg-white border rounded shadow">
      {children}
    </div>
  );
}
export function DropdownMenuLabel({ children }) {
  return <div className="px-2 py-1 text-xs text-gray-500">{children}</div>;
}
export function DropdownMenuItem({ children, ...props }) {
  return (
    <div className="px-4 py-2 hover:bg-gray-100 cursor-pointer" {...props}>
      {children}
    </div>
  );
}
export function DropdownMenuSeparator() {
  return <hr className="my-1" />;
}
