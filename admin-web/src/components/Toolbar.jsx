export default function Toolbar({ title, description, children }) {
  return (
    <div className="toolbar">
      <div>
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
      </div>
      {children ? <div className="toolbar-actions">{children}</div> : null}
    </div>
  );
}
