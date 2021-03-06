DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT USAGE ON SCHEMA public TO user1;

CREATE TABLE groups (
	id SERIAL PRIMARY KEY,
	is_variable BOOLEAN,
	is_term BOOLEAN,
	is_hedge BOOLEAN
);

CREATE TABLE synonims (
	id SERIAL PRIMARY KEY,
	group_id INT NOT NULL REFERENCES groups(id),
	lemma VARCHAR(255),
	grammemes VARCHAR(255),
	hits INT
);

CREATE TABLE variables (
	id SERIAL PRIMARY KEY,
	name_id INT NOT NULL REFERENCES groups(id),
	name VARCHAR(255),
	validated BOOLEAN,
	min REAL, 
	max REAL 
);

CREATE TABLE functions (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE terms (
	id SERIAL PRIMARY KEY,
	name_id INT NOT NULL REFERENCES groups(id),
	name VARCHAR(255),
	validated BOOLEAN,
	function_id INT NOT NULL REFERENCES functions(id),
	points VARCHAR(255)
);

CREATE TABLE variables_terms (
	variable_id INT NOT NULL REFERENCES variables(id) ON DELETE CASCADE,
	term_id INT NOT NULL REFERENCES terms(id) ON DELETE CASCADE
);

CREATE TABLE hedges (
	id SERIAL PRIMARY KEY,
	name_id INT NOT NULL REFERENCES groups(id),
	name VARCHAR(255),
	validated BOOLEAN,
	result VARCHAR(255)
);

CREATE TABLE variables_hedges (
	variable_id INT NOT NULL REFERENCES variables(id) ON DELETE CASCADE,
	hedge_id INT NOT NULL REFERENCES hedges(id) ON DELETE CASCADE
);

CREATE TABLE types (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255)
);

CREATE TABLE nodes (
	id SERIAL PRIMARY KEY,
	parent_id INT NULL REFERENCES nodes(id),
	type_id INT NOT NULL REFERENCES types(id),
	variable_id INT NULL REFERENCES variables(id) ON DELETE CASCADE,
	term_id INT NULL REFERENCES terms(id) ON DELETE CASCADE,
	hedge_id INT NULL REFERENCES hedges(id) ON DELETE CASCADE
);

CREATE TABLE closures (
	ancestor_id INT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
	descendant_id INT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
	PRIMARY KEY (ancestor_id, descendant_id)
);

CREATE TABLE rules (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255),
	validated BOOLEAN,
	antecedent_id INT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
	consequent_id INT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE
);

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO user1;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO user1;

INSERT INTO groups (is_variable, is_term, is_hedge) VALUES
	(true, false, false),
	(true, false, false),
	(true, false, false),
	(false, true, false),
	(false, true, false),
	(false, true, false),
	(false, false, true);

INSERT INTO synonims (group_id, lemma, grammemes, hits) VALUES
	(1, 'возраст', 'сущ еч', 1),
	(1, 'годы', 'сущ мч', 1),
	(2, 'время', 'сущ еч', 1),
	(2, 'часы', 'сущ мч', 1),
	(3, 'активность', 'сущ еч', 1),
	(4, 'молодой', 'прил', 1),
	(4, 'юный', 'прил', 1),
	(5, 'поздний', 'прил', 1),
	(6, 'низкий', 'прил', 1),
	(7, 'не', 'част', 1);

INSERT INTO variables (name_id, name, validated, min, max) VALUES 
	(1, '', false, 0, 100),
	(2, '', false, 0, 24),
	(3, '', false, 0, 10);

INSERT INTO functions (name) VALUES 
	('трапеция');

INSERT INTO terms (name_id, name, validated, function_id, points) VALUES 
	(4, '', false, 1, '15;20;25;30'),
	(5, '', false, 1, '0;1;3;4'),
	(6, '', false, 1, '0;1;2;3');

INSERT INTO variables_terms (variable_id, term_id) VALUES
	(1, 1),
	(2, 2),
	(3, 3);

INSERT INTO hedges (name_id, name, validated, result) VALUES 
	(7, '', false, '1 - x');

INSERT INTO variables_hedges (variable_id, hedge_id) VALUES 
	(1, 1);

INSERT INTO types (name) VALUES 
	('variable'),
	('hedge'),
	('term'),
	('term_complex'),
	('variable_value'),
	('term_and'),
	('term_or'),
	('variable_and'),
	('variable_or'),
	('variable_not');

INSERT INTO nodes (parent_id, type_id, variable_id, term_id, hedge_id) VALUES
	(null, 8, null, null, null), (1, 5, null, null, null), 
	(2, 1, 1, null, null), (2, 4, null, null, null), 
	(4, 2, null, null, 1), (4, 3, null, 1, null), 
	(1, 5, null, null, null), (7, 1, 2, null, null), 
	(7, 3, null, 2, null), (null, 5, null, null, null), 
	(10, 1, 3, null, null), (10, 3, null, 3, null);

INSERT INTO closures (ancestor_id, descendant_id) VALUES
	(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
	(1, 8), (1, 9), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
	(3, 3), (4, 4), (4, 5), (4, 6), (5, 5), (6, 6), (7, 7), 
	(7, 8), (7, 9), (8, 8), (9, 9), (10, 10), (10, 11), 
	(10, 12), (11, 11), (12, 12);

INSERT INTO rules (name, validated, antecedent_id, consequent_id) VALUES 
	('ЕСЛИ возраст не молодой и время позднее, TO активность низкая', false, 1, 10);
