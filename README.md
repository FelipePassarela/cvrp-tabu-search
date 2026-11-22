# CVRP com busca tabu

O repositório reúne o código, as instâncias e o material de referência para a resolução do Problema de Roteamento de Veículos Capacitados (CVRP) com busca tabu.

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

## Distribuição

Use `uv build` para gerar o wheel e a distribuição de código-fonte em `dist/`.
