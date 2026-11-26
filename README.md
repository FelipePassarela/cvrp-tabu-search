# CVRP com busca tabu

O repositório reúne experimentos de busca tabu para o Problema de Roteamento de Veículos Capacitados (CVRP).

As instâncias adicionais estão em [`benchmarks/general/`](benchmarks/general/) e [`benchmarks/selected/`](benchmarks/selected/). O material de consulta está em [`references/`](references/).

## Instalação

Na raiz do repositório, use o [uv](https://docs.astral.sh/uv/getting-started/installation/) para criar o ambiente com Python 3.12 e instalar os pacotes do workspace.

```sh
uv sync --locked --all-packages
```

## Execução

```sh
uv run --locked --package cvrp-search cvrp-search --help
uv run --locked --package cvrp-search cvrp-search
uv run --locked --package cvrp-search cvrp-search benchmarks/general/A-n33-k5.vrp --seed 1
```

`cvrp-search` executa a busca tabu com inversões, realocações e trocas. Por padrão, usa a instância `A-n32-k5.vrp`, incluída no [pacote da CLI](packages/search/src/cvrp_search/data/). A primeira linha da saída reúne o melhor custo, o custo ótimo informado no arquivo `.vrp` e o gap absoluto e percentual. Sem valor de referência, o ótimo e o gap aparecem como `N/A`. Em seguida, a CLI mostra o total de iterações e os clientes de cada rota utilizada na ordem de visita. O depósito é implícito nas duas extremidades de cada rota.

Use `--max-iterations` e `--stagnation-limit` para ajustar os critérios de parada. Os padrões são 60 iterações e 30 iterações consecutivas sem melhora. Com `--max-iterations 0`, o comando exibe a solução inicial.

Use `--tabu-tenure-min` e `--tabu-tenure-max` para configurar o intervalo inclusivo de duração tabu, que por padrão vai de 1 a 15. Use valores iguais para fixar a duração ou dois zeros para desativar o bloqueio tabu. Use `--seed` para reproduzir os sorteios.

O comando `cvrp` continua disponível como alias. Também é possível executar a CLI com `uv run --locked --package cvrp-search python -m cvrp_search`.

## Desenvolvimento

Os pacotes têm metadados próprios e compartilham o `uv.lock` da raiz.

- [`cvrp-core`](packages/core/) contém os modelos de domínio e as classes de busca, incluindo a representação de instâncias e soluções, os movimentos de vizinhança e a busca tabu.
- [`cvrp-search`](packages/search/) contém a CLI, que carrega a instância, executa a busca de `cvrp-core` e exibe o resultado.

Os testes de domínio e busca ficam em [`packages/core/tests/`](packages/core/tests/). Os testes da CLI ficam em [`packages/search/tests/`](packages/search/tests/).

Execute os testes com pytest. Use Ruff para lint e formatação e ty para checagem de tipos.

```sh
uv run --locked --all-packages pytest
uv run --locked ruff check
uv run --locked ruff format --check
uv run --locked --all-packages ty check
uv run --locked --all-packages lint-imports --no-cache
```

O Import Linter verifica que a dependência entre os pacotes segue da CLI para o core. O GitHub Actions roda essa checagem nas PRs e nos pushes para `main`.

Ative os hooks em cada clone. O Ruff verifica o lint e a formatação dos arquivos preparados para commit. O ty analisa o projeto inteiro quando há alterações em código Python ou na configuração do ambiente. O pytest executa a suíte completa antes de o Git gravar um commit de merge local automático.

```sh
uv run --locked pre-commit install
uv run --locked pre-commit run --all-files
uv run --locked pre-commit run --all-files --hook-stage pre-merge-commit
```

## Distribuição

Use `uv build --all-packages` para gerar os wheels e as distribuições de código-fonte em `dist/`.
