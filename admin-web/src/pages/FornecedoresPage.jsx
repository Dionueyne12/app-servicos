import Toolbar from "../components/Toolbar.jsx";

export default function FornecedoresPage() {
  return (
    <section>
      <Toolbar title="Fornecedores" description="Base inicial para comercios, ferragistas e depositos." />
      <article className="panel empty-module">
        <h2>Modulo preparado</h2>
        <p>
          Esta area esta reservada para lojas parceiras, catalogo de materiais,
          estoque, valores a receber e aprovacao de comercios.
        </p>
        <div className="placeholder-grid">
          <div><strong>Nome da loja</strong><span>Futuro cadastro</span></div>
          <div><strong>Materiais vendidos</strong><span>Relatorio futuro</span></div>
          <div><strong>Valor a receber</strong><span>Repasses futuros</span></div>
        </div>
      </article>
    </section>
  );
}
