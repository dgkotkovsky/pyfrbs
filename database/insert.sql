INSERT INTO variables (name, min, max) VALUES 
	('возраст', 0, 100),
	('время', 0, 24),
	('активность', 0, 10);

INSERT INTO functions (type) VALUES 
	('трапеция');

INSERT INTO terms (value, function_id, points) VALUES 
	('молодой', 1, '15:20:25:30'),
	('позднее', 1, '0:1:3:4'),
	('низкая', 1, '0:1:2:3');

INSERT INTO variables_terms (variable_id, term_id) VALUES
	(1, 1),
	(2, 2),
	(3, 3);

INSERT INTO hedges (value, result) VALUES 
	('не', '1 - x');

INSERT INTO variables_hedges (variable_id, hedge_id) VALUES 
	(1, 1);

INSERT INTO types (name) VALUES 
	('term'),
	('hedge'),
	('variable'),
	('term_complex'),
	('variable_value'),
	('term_and'),
	('term_or'),
	('variable_and'),
	('variable_or'),
	('variable_not');

INSERT INTO nodes (id, parent_id, type_id, variable_id, term_id, hedge_id) VALUES
	(1, 1, 8, 0, 0, 0), (2, 1, 5, 0, 0, 0), (3, 2, 3, 1, 0, 0), 
	(4, 2, 4, 0, 0, 0), (5, 4, 2, 0, 0, 1), (6, 4, 1, 0, 1, 0), 
	(7, 1, 5, 0, 0, 0), (8, 7, 3, 2, 0, 0), (9, 7, 1, 0, 2, 0), 
	(10, 10, 5, 0, 0, 0), (11, 10, 3, 3, 0, 0), (12, 10, 1, 0, 3, 0);

INSERT INTO closures (ancestor_id, descendant_id) VALUES
	(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
	(1, 8), (1, 9), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
	(3, 3), (4, 4), (4, 5), (4, 6), (5, 5), (6, 6), (7, 7), 
	(7, 8), (7, 9), (8, 8), (9, 9), (10, 10), (10, 11), 
	(10, 12), (11, 11), (12, 12);

INSERT INTO rules (name, antecedent_id, consequent_id) VALUES 
	('молодёжь по ночам не спит', 1, 10);
