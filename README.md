# CVRP com busca tabu

O repositório reúne experimentos de busca tabu para o Problema de Roteamento de Veículos Capacitados (CVRP).

As instâncias adicionais estão em [`benchmarks/general/`](benchmarks/general/) e [`benchmarks/selected/`](benchmarks/selected/). O material de consulta está em [`references/`](references/).

## Instalação

Na raiz do repositório, use o [uv](https://docs.astral.sh/uv/getting-started/installation/) para criar o ambiente com Python 3.12 e instalar o pacote.

```sh
uv sync --locked
```

## Execução

```sh
uv run cvrp-baseline
uv run cvrp-tabu-search
```

O primeiro comando executa o experimento original com inversões dentro de cada rota. O segundo executa a variante com movimentos entre rotas, intensificação e diversificação. Ambos usam a instância `A-n32-k5.vrp`, incluída em [`src/cvrp_tabu_search/data/`](src/cvrp_tabu_search/data/), e gravam os resultados em CSV e PNG no diretório de trabalho.

Os resultados usam os prefixos `runs_`, `history_`, `convergence_` e `ttt_`. A variante com movimentos entre rotas inclui `tabu_` antes do nome da instância.

## Desenvolvimento

Use Ruff para lint e formatação e ty para checagem de tipos.

```sh
uv run ruff check
uv run ruff format --check
uv run ty check
```

## Distribuição

Use `uv build` para gerar o wheel e a distribuição de código-fonte em `dist/`.
