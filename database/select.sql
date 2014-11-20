SELECT DISTINCT variable.name, variable.min, variable.max, term.value, term.points, function.type, hedge.value, hedge.result FROM variable, variable_term, term, function, variable_hedge, hedge WHERE variable.id = variable_term.variable_id AND term.id = variable_term.term_id;
SELECT * FROM rule;
SELECT * FROM node
  JOIN closure ON (node.id = closure.descendant_id)
WHERE closure.ancestor_id = 1;
SELECT * FROM node
  JOIN closure ON (node.id = closure.descendant_id)
WHERE closure.ancestor_id = 10;
