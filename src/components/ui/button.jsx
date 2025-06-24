export function Button({ children, variant, ...props }) {
  const base = 'px-4 py-2 rounded border';
  const styles = {
    default: base + ' bg-blue-600 text-white',
    ghost: base + ' bg-transparent',
  };
  const className = styles[variant] || base;
  return (
    <button className={className} {...props}>
      {children}
    </button>
  );
}
