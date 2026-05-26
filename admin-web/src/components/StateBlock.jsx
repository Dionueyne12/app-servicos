export function LoadingBlock({ message = "Carregando..." }) {
  return <div className="state-block">{message}</div>;
}

export function ErrorBlock({ message, onRetry }) {
  if (!message) return null;
  return (
    <div className="error-block">
      <span>{message}</span>
      {onRetry ? <button type="button" className="ghost-button" onClick={onRetry}>Tentar novamente</button> : null}
    </div>
  );
}
