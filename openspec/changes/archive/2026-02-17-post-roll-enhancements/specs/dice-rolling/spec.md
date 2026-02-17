## MODIFIED Requirements

### Requirement: Sugerir melhor combinação (best mode)

Quando best mode está habilitado, o bot SHALL primeiro exibir todos os resultados individuais dos dados com tamanho e valor, e depois calcular e exibir as combinações mais relevantes de 2 dados para total + 1 dado para effect die. SHALL exibir pelo menos: a combinação com maior total e a combinação com maior effect die. Dados que rolaram 1 (hitches) SHALL ser excluídos das sugestões mas SHALL aparecer na lista de resultados individuais marcados como hitch.

#### Scenario: Best mode com 4 dados

- **WHEN** best mode habilitado e resultado é d10:7, d8:5, d6:4, d6:3
- **THEN** bot exibe primeiro todos os resultados: "d10 tirou 7, d8 tirou 5, d6 tirou 4, d6 tirou 3."
- **AND** depois exibe "Melhor total: d10 com 7 mais d8 com 5, igual a 12. Effect die: d6." e "Maior effect: d10 com 7 mais d6 com 3, igual a 10. Effect die: d8."

#### Scenario: Best mode com hitches

- **WHEN** best mode habilitado e d6:1 entre os resultados
- **THEN** bot exibe todos os resultados individuais incluindo "d6 tirou 1 (hitch)"
- **AND** d6 com hitch é excluído das combinações sugeridas para total e effect die.

#### Scenario: Best mode desabilitado

- **WHEN** best mode desabilitado
- **THEN** bot exibe apenas os resultados individuais sem sugestões de combinação.
