#!/usr/bin/env python

import sys
import psycopg2

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QTreeWidgetItem
from PyQt5.uic import loadUi

class Window(QMainWindow):
    def __init__(self, *args):
        super(Window, self).__init__(*args)

        self.conn = psycopg2.connect(host='127.0.0.1', database='fuzzy', user='user1', password='pass1')

        loadUi('fuzzy.ui', self)

        # Initialize variables tab

        self.fillComboWithLemmas(self.uiVariablesCombo, 'variables')
        self.uiVariablesCombo.currentIndexChanged.connect(self.onVariableSelected)
        self.uiCreateVariableButton.clicked.connect(self.onCreateVariableClicked)
        self.uiDeleteVariableButton.clicked.connect(self.onDeleteVariableClicked)

        self.uiRangeMinEdit.textEdited.connect(self.checkRange)
        self.uiRangeMinEdit.setValidator(QDoubleValidator(-1000000, 1000000, 2, self.uiRangeMinEdit))
        self.uiRangeMaxEdit.textEdited.connect(self.checkRange)
        self.uiRangeMaxEdit.setValidator(QDoubleValidator(-1000000, 1000000, 2, self.uiRangeMaxEdit))

        self.loadTerms()
        self.uiTermsCombo.currentIndexChanged.connect(self.onTermSelected)
        self.uiAddTermButton.clicked.connect(self.onAddTermClicked)
        self.uiTermsList.clicked.connect(self.onVariableTermSelected)
        self.uiRemoveTermButton.clicked.connect(self.onRemoveTermClicked)

        self.loadHedges()
        self.uiHedgesCombo.currentTextChanged.connect(self.onHedgeSelected)
        self.uiAddHedgeButton.clicked.connect(self.onAddHedgeClicked)
        self.uiHedgesList.clicked.connect(self.onVariableHedgeSelected)
        self.uiRemoveHedgeButton.clicked.connect(self.onRemoveHedgeClicked)

        self.uiCommitVariableButton.clicked.connect(self.commitVariable)

        # Initialize terms tab

        self.fillComboWithLemmas(self.uiTerms2Combo, 'terms')
        self.uiTerms2Combo.currentIndexChanged.connect(self.onTerm2Selected)
        self.uiCreateTermButton.clicked.connect(self.onCreateTermClicked)
        self.uiDeleteTermButton.clicked.connect(self.onDeleteTermClicked)

        self.fillComboWithNames(self.uiFunctionCombo, 'functions')
        self.uiFunctionCombo.currentIndexChanged.connect(self.onFunctionSelected)

        self.uiPointsEdit.textEdited.connect(self.checkPoints)

        self.uiCommitTermButton.clicked.connect(self.commitTerm)

        # Initialize hedges tab

        self.fillComboWithLemmas(self.uiHedgesCombo, 'hedges')
        self.uiHedgesCombo.currentIndexChanged.connect(self.onHedge2Selected)
        self.uiCreateHedgeButton.clicked.connect(self.onCreateHedgeClicked)
        self.uiDeleteHedgeButton.clicked.connect(self.onDeleteHedgeClicked)

        self.uiResultEdit.textEdited.connect(self.onResultChanged)

        self.uiCommitHedgeButton.clicked.connect(self.commitHedge)

        # Initialize rules tab

        self.fillComboWithNames(self.uiRulesCombo, 'rules')
        self.uiRulesCombo.currentIndexChanged.connect(self.onRuleSelected)
        self.uiCreateRuleButton.clicked.connect(self.onCreateRuleClicked)
        self.uiDeleteRuleButton.clicked.connect(self.onDeleteRuleClicked)

        self.uiCommitRuleButton.clicked.connect(self.commitRule)

        # Initialize main window

        self.uiTabs.setCurrentIndex(0)
        self.uiTabs.currentChanged.connect(self.onTabChanged)

    def getLemmas(self, group):
        cur = self.conn.cursor()
        cur.execute('SELECT lemma FROM synonims WHERE group_id = %s ORDER BY hits DESC;', (group,))
        lemmas = []
        for row in cur.fetchall():
            lemmas.append(row[0])
        cur.close()
        return lemmas

    def fillComboWithLemmas(self, combo, table):
        combo.clear()
        cur = self.conn.cursor()
        cur.execute('SELECT id, name_id FROM %s;' % table)
        for row in cur.fetchall():
            combo.addItem(', '.join(self.getLemmas(row[1])), row[0])
        cur.close()
        combo.setCurrentIndex(-1)

    def fillComboWithNames(self, combo, table):
        combo.clear()
        cur = self.conn.cursor()
        cur.execute('SELECT id, name FROM %s;' % table)
        for row in cur.fetchall():
            combo.addItem(row[1], row[0])
        cur.close()
        combo.setCurrentIndex(-1)

    # Actions on variables tab

    def loadTerms(self):
        self.fillComboWithLemmas(self.uiTermsCombo, 'terms')
        self.uiAddTermButton.setEnabled(False)

    def loadHedges(self):
        self.fillComboWithLemmas(self.uiHedgesCombo, 'hedges')
        self.uiAddHedgeButton.setEnabled(False)

    def onVariableSelected(self):
        if (self.uiVariablesCombo.isEditable() == True):
            return

        self.uiTermsCombo.setCurrentIndex(-1)
        self.uiAddTermButton.setEnabled(False)
        self.uiRemoveTermButton.setEnabled(False)
        self.uiHedgesCombo.setCurrentIndex(-1)
        self.uiAddHedgeButton.setEnabled(False)
        self.uiRemoveHedgeButton.setEnabled(False)
        self.uiCommitVariableButton.setEnabled(False)

        self.uiRangeMinEdit.clear()
        self.uiRangeMaxEdit.clear()
        self.uiTermsList.clear()
        self.uiHedgesList.clear()

        if (self.uiVariablesCombo.currentIndex() == -1):
            self.uiRenameVariableButton.setEnabled(False)
            self.uiDeleteVariableButton.setEnabled(False)
            self.uiRangeMinEdit.setEnabled(False)
            self.uiRangeMaxEdit.setEnabled(False)
            self.uiTermsCombo.setEnabled(False)
            self.uiTermsList.setEnabled(False)
            self.uiHedgesCombo.setEnabled(False)
            self.uiHedgesList.setEnabled(False)
            return

        if (self.uiVariablesCombo.currentData() != 0):
            cur = self.conn.cursor()
            cur.execute('SELECT terms.id, terms.name_id FROM variables, terms, variables_terms WHERE variables.id = %s AND variables.id = variables_terms.variable_id AND terms.id = variables_terms.term_id;', (self.uiVariablesCombo.currentData(),))
            for row in cur.fetchall():
                item = QListWidgetItem(', '.join(self.getLemmas(row[1])))
                item.setData(Qt.UserRole, row[0])
                self.uiTermsList.addItem(item)
            cur.close()
            self.loadTerms()

            cur = self.conn.cursor()
            cur.execute('SELECT hedges.id, hedges.name_id FROM variables, hedges, variables_hedges WHERE variables.id = %s AND variables.id = variables_hedges.variable_id AND hedges.id = variables_hedges.hedge_id;', (self.uiVariablesCombo.currentData(),))
            for row in cur.fetchall():
                item = QListWidgetItem(', '.join(self.getLemmas(row[1])))
                item.setData(Qt.UserRole, row[0])
                self.uiHedgesList.addItem(item)
            cur.close()
            self.loadHedges()

            cur = self.conn.cursor()
            cur.execute('SELECT variables.min, variables.max FROM variables WHERE variables.id = %s;', (self.uiVariablesCombo.currentData(),))
            range = cur.fetchone()
            if (range):
                self.uiRangeMinEdit.setText('%s' % range[0])
                self.uiRangeMaxEdit.setText('%s' % range[1])

        self.uiRenameVariableButton.setEnabled(True)
        self.uiDeleteVariableButton.setEnabled(True)
        self.uiRangeMinEdit.setEnabled(True)
        self.uiRangeMaxEdit.setEnabled(True)
        self.uiTermsCombo.setEnabled(True)
        self.uiTermsList.setEnabled(True)
        self.uiHedgesCombo.setEnabled(True)
        self.uiHedgesList.setEnabled(True)

    def onTermSelected(self):
        self.uiAddTermButton.setEnabled(True)

    def onVariableTermSelected(self):
        self.uiRemoveTermButton.setEnabled(True)

    def onAddTermClicked(self):
        found = False
        for index in range(self.uiTermsList.count()):
            if (self.uiTermsList.item(index).data(Qt.UserRole) == self.uiTermsCombo.currentData()):
                found = True
                break
        if (not found):
            item = QListWidgetItem(self.uiTermsCombo.currentText())
            item.setData(Qt.UserRole, self.uiTermsCombo.currentData())
            self.uiTermsList.addItem(item)
            self.checkRange()

    def onRemoveTermClicked(self):
        self.uiTermsList.takeItem(self.uiTermsList.currentRow())
        if (self.uiTermsList.count() == 0):
            self.uiRemoveTermButton.setEnabled(False)
        self.checkRange()

    def onHedgeSelected(self):
        self.uiAddHedgeButton.setEnabled(True)

    def onVariableHedgeSelected(self):
        self.uiRemoveHedgeButton.setEnabled(True)

    def onAddHedgeClicked(self):
        found = False
        for index in range(self.uiHedgesList.count()):
            if (self.uiHedgesList.item(index).data(Qt.UserRole) == self.uiHedgesCombo.currentData()):
                found = True
                break
        if (not found):
            item = QListWidgetItem(self.uiHedgesCombo.currentText())
            item.setData(Qt.UserRole, self.uiHedgesCombo.currentData())
            self.uiHedgesList.addItem(item)
            self.checkRange()

    def onRemoveHedgeClicked(self):
        self.uiHedgesList.takeItem(self.uiHedgesList.currentRow())
        if (self.uiHedgesList.count() == 0):
            self.uiRemoveHedgeButton.setEnabled(False)
        self.checkRange()

    def onCreateVariableClicked(self):
        self.uiVariablesCombo.setCurrentIndex(-1)
        self.uiVariablesCombo.setEditable(True)
        self.uiVariablesCombo.lineEdit().returnPressed.connect(self.onVariableEntered)
        self.uiVariablesCombo.setFocus()
        self.uiCreateVariableButton.setEnabled(False)

    def onVariableEntered(self):
        self.uiVariablesCombo.setEditable(False)
        self.uiCreateVariableButton.setEnabled(True)
        self.uiVariablesCombo.setItemData(self.uiVariablesCombo.currentIndex(), 0)
        self.onVariableSelected()

    def onDeleteVariableClicked(self):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM variables WHERE id = %s;', (self.uiVariablesCombo.currentData(),))
        self.conn.commit()
        cur.close()
        self.uiVariablesCombo.removeItem(self.uiVariablesCombo.currentIndex())

    def checkRange(self):
        if (self.uiRangeMinEdit.text() != '' and self.uiRangeMaxEdit.text() != ''):
            self.uiCommitVariableButton.setEnabled(True)
        else:
            self.uiCommitVariableButton.setEnabled(False)

    def commitVariable(self):
        self.uiCommitVariableButton.setEnabled(False)
        cur = self.conn.cursor()
        variable_id = self.uiVariablesCombo.currentData()
        if (variable_id):
            cur.execute('UPDATE variables SET min = %s, max = %s WHERE id = %s;', (self.uiRangeMinEdit.text(), self.uiRangeMaxEdit.text(), variable_id))
            cur.execute('DELETE FROM variables_terms WHERE variable_id = %s;', (variable_id,))
            cur.execute('DELETE FROM variables_hedges WHERE variable_id = %s;', (variable_id,))
        else:
            cur.execute('INSERT INTO groups (is_variable, is_term, is_hedge) VALUES (true, false, false) RETURNING id;')
            group_id = cur.fetchone()[0]
            for lemma in self.uiVariablesCombo.currentText().replace(' ', '').split(','):
                cur.execute('INSERT INTO synonims (group_id, lemma, grammemes, hits) VALUES (%s, %s, %s, 0);', (group_id, lemma, ''));
            cur.execute('INSERT INTO variables (name_id, min, max) VALUES (%s, %s, %s) RETURNING id;', (group_id, self.uiRangeMinEdit.text(), self.uiRangeMaxEdit.text()))
            variable_id = cur.fetchone()[0]
            self.uiVariablesCombo.setItemData(self.uiVariablesCombo.currentIndex(), variable_id)
        for i in range(0, self.uiTermsList.count()):
            cur.execute('INSERT INTO variables_terms (variable_id, term_id) VALUES (%s, %s);', (variable_id, self.uiTermsList.item(i).data(Qt.UserRole)))
        for j in range(0, self.uiHedgesList.count()):
            cur.execute('INSERT INTO variables_hedges (variable_id, hedge_id) VALUES (%s, %s);', (variable_id, self.uiHedgesList.item(j).data(Qt.UserRole)))
        self.conn.commit()
        cur.close()

    # Actions on terms tab

    def onTerm2Selected(self):
        if (self.uiTerms2Combo.isEditable() == True):
            return

        self.uiCommitTermButton.setEnabled(False)

        self.uiPointsEdit.clear()

        if (self.uiTerms2Combo.currentIndex() == -1):
            self.uiRenameTermButton.setEnabled(False)
            self.uiDeleteTermButton.setEnabled(False)
            self.uiFunctionCombo.setCurrentIndex(-1)
            self.uiFunctionCombo.setEnabled(False)
            self.uiPointsEdit.setEnabled(False)
            return

        if (self.uiTerms2Combo.currentData() != 0):
            self.uiFunctionCombo.blockSignals(True)
            cur = self.conn.cursor()
            cur.execute('SELECT functions.name FROM terms, functions WHERE functions.id = terms.function_id AND terms.id = %s;', (self.uiTerms2Combo.currentData(),))
            name = cur.fetchone()
            if (name):
                self.uiFunctionCombo.setCurrentText(name[0])
            else:
                self.uiFunctionCombo.setCurrentIndex(-1)
            self.uiFunctionCombo.blockSignals(False)

            cur = self.conn.cursor()
            cur.execute('SELECT points FROM terms WHERE id = %s;', (self.uiTerms2Combo.currentData(),))
            points = cur.fetchone()
            if (points):
                self.uiPointsEdit.setText('%s' % points[0])

        self.uiRenameTermButton.setEnabled(True)
        self.uiDeleteTermButton.setEnabled(True)
        self.uiPointsEdit.setEnabled(True)
        self.uiFunctionCombo.setEnabled(True)

    def onCreateTermClicked(self):
        self.uiTerms2Combo.setCurrentIndex(-1)
        self.uiTerms2Combo.setEditable(True)
        self.uiTerms2Combo.lineEdit().returnPressed.connect(self.onTermEntered)
        self.uiTerms2Combo.setFocus()
        self.uiCreateTermButton.setEnabled(False)

    def onTermEntered(self):
        self.uiTerms2Combo.setEditable(False)
        self.uiCreateTermButton.setEnabled(True)
        self.uiTerms2Combo.setItemData(self.uiTerms2Combo.currentIndex(), 0)
        self.onTerm2Selected()
        self.uiFunctionCombo.setFocus()

    def onDeleteTermClicked(self):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM terms WHERE id = %s;', (self.uiTerms2Combo.currentData(),))
        self.conn.commit()
        cur.close()
        self.uiTerms2Combo.removeItem(self.uiTerms2Combo.currentIndex())

    def checkPoints(self):
        if (self.uiPointsEdit.text() != ''):
            self.uiCommitTermButton.setEnabled(True)
        else:
            self.uiCommitTermButton.setEnabled(False)

    def onFunctionSelected(self):
        if (self.uiFunctionCombo.currentIndex() != -1):
            self.checkPoints()

    def commitTerm(self):
        self.uiCommitTermButton.setEnabled(False)
        cur = self.conn.cursor()
        term_id = self.uiTerms2Combo.currentData()
        if (term_id):
            cur.execute('UPDATE terms SET function_id = %s, points = %s WHERE id = %s;', (self.uiFunctionCombo.currentData(), self.uiPointsEdit.text(), term_id))
        else:
            cur.execute('INSERT INTO groups (is_variable, is_term, is_hedge) VALUES (false, true, false) RETURNING id;')
            group_id = cur.fetchone()[0]
            for lemma in self.uiTerms2Combo.currentText().replace(' ', '').split(','):
                cur.execute('INSERT INTO synonims (group_id, lemma, grammemes, hits) VALUES (%s, %s, %s, 0);', (group_id, lemma, ''));
            cur.execute('INSERT INTO terms (name_id, function_id, points) VALUES (%s, %s, %s) RETURNING id;', (group_id, self.uiFunctionCombo.currentData(), self.uiPointsEdit.text()))
            term_id = cur.fetchone()[0]
            self.uiTerms2Combo.setItemData(self.uiTerms2Combo.currentIndex(), term_id)
        self.conn.commit()
        cur.close()

    # Actions on hedges tab

    def onHedge2Selected(self):
        if (self.uiHedgesCombo.isEditable() == True):
            return

        self.uiCommitHedgeButton.setEnabled(False)

        if (self.uiHedgesCombo.currentIndex() == -1):
            self.uiRenameHedgeButton.setEnabled(False)
            self.uiDeleteHedgeButton.setEnabled(False)
            self.uiResultEdit.clear()
            self.uiResultEdit.setEnabled(False)
            return

        cur = self.conn.cursor()
        cur.execute('SELECT result FROM hedges WHERE value = %s;', (self.uiHedgesCombo.currentText(),))
        result = cur.fetchone()
        if (result):
            self.uiResultEdit.setText('%s' % result[0])
        else:
            self.uiResultEdit.clear()

        self.uiRenameHedgeButton.setEnabled(True)
        self.uiDeleteHedgeButton.setEnabled(True)
        self.uiResultEdit.setEnabled(True)

    def onCreateHedgeClicked(self):
        self.uiHedgesCombo.setCurrentIndex(-1)
        self.uiHedgesCombo.setEditable(True)
        self.uiHedgesCombo.lineEdit().returnPressed.connect(self.onHedgeEntered)
        self.uiHedgesCombo.setFocus()
        self.uiCreateHedgeButton.setEnabled(False)

    def onHedgeEntered(self):
        self.uiHedgesCombo.setEditable(False)
        self.uiCreateHedgeButton.setEnabled(True)
        self.onHedge2Selected()
        self.uiResultEdit.setFocus()

    def onDeleteHedgeClicked(self):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM hedges WHERE value = %s;', (self.uiHedgesCombo.currentText(),))
        self.conn.commit()
        cur.close()
        self.uiHedgesCombo.removeItem(self.uiHedgesCombo.currentIndex())

    def onResultChanged(self):
        self.uiCommitHedgeButton.setEnabled(True)

    def commitHedge(self):
        self.uiCommitHedgeButton.setEnabled(False)
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM hedges WHERE value = %s', (self.uiHedgesCombo.currentText(),))
        hedge_id = cur.fetchone()
        if (hedge_id):
            cur.execute('UPDATE hedges SET result = %s WHERE id = %s;', (self.uiResultEdit.text(), hedge_id))
        else:
            cur.execute('INSERT INTO hedges (value, result) VALUES (%s, %s);', (self.uiHedgesCombo.currentText(), self.uiResultEdit.text()))
        self.conn.commit()
        cur.close()

    def onRuleSelected(self):
        if (self.uiRulesCombo.isEditable() == True):
            return

        self.uiCommitRuleButton.setEnabled(False)

        self.uiAntecedentTree.clear()
        self.uiConsequentTree.clear()

        if (self.uiRulesCombo.currentIndex() == -1):
            self.uiRenameRuleButton.setEnabled(False)
            self.uiDeleteRuleButton.setEnabled(False)
            self.uiAntecedentNodeTypesCombo.setEnabled(False)
            self.uiAntecedentNodesCombo.setEnabled(False)
            self.uiAntecedentTree.setEnabled(False)
            self.uiConsequentNodeTypesCombo.setEnabled(False)
            self.uiConsequentNodesCombo.setEnabled(False)
            self.uiConsequentTree.setEnabled(False)
            return

        cur = self.conn.cursor()
        cur.execute('SELECT nodes.id, types.name FROM rules, nodes, types WHERE rules.name = %s AND rules.antecedent_id = nodes.id AND types.id = nodes.type_id;', (self.uiRulesCombo.currentText(),))
        root = cur.fetchone()
        cur.close()
        if (root):
            item = QTreeWidgetItem()
            item.setText(0, '%s' % root[1])
            item.setText(1, '%s' % root[0])
            self.uiAntecedentTree.addTopLevelItem(item)
            cur = self.conn.cursor()
            cur.execute('SELECT nodes.id, nodes.parent_id, types.name FROM nodes, types, closures WHERE nodes.id = closures.descendant_id AND closures.ancestor_id IN (SELECT antecedent_id FROM rules WHERE name = %s) AND nodes.type_id = types.id ORDER BY parent_id ASC;', (self.uiRulesCombo.currentText(),))
            nodes = cur.fetchall()
            cur.close()
            for node in nodes:
                if node[0] != node[1]:
                    if (node[2] == 'variable'):
                        cur = self.conn.cursor()
                        cur.execute('SELECT variables.name FROM variables, nodes WHERE variables.id = nodes.variable_id AND nodes.id = %s;', (node[0],))
                        name = cur.fetchone()
                        cur.close()
                    elif (node[2] == 'hedge'):
                        cur = self.conn.cursor()
                        cur.execute('SELECT hedges.value FROM hedges, nodes WHERE hedges.id = nodes.hedge_id AND nodes.id = %s;', (node[0],))
                        name = cur.fetchone()
                        cur.close()
                    elif (node[2] == 'term'):
                        cur = self.conn.cursor()
                        cur.execute('SELECT terms.value FROM terms, nodes WHERE terms.id = nodes.term_id AND nodes.id = %s;', (node[0],))
                        name = cur.fetchone()
                        cur.close()
                    else:
                        name = node[2]
                    parents = self.uiAntecedentTree.findItems('%s' % node[1], Qt.MatchExactly | Qt.MatchRecursive, 1)
                    item = QTreeWidgetItem()
                    item.setText(0, '%s' % name)
                    item.setText(1, '%s' % node[0])
                    parents[0].addChild(item)

        cur = self.conn.cursor()
        cur.execute('SELECT nodes.id, types.name FROM rules, nodes, types WHERE rules.name = %s AND rules.consequent_id = nodes.id AND types.id = nodes.type_id;', (self.uiRulesCombo.currentText(),))
        root = cur.fetchone()
        cur.close()
        if (root):
            item = QTreeWidgetItem()
            item.setText(0, '%s' % root[1])
            item.setText(1, '%s' % root[0])
            self.uiConsequentTree.addTopLevelItem(item)
            cur = self.conn.cursor()
            cur.execute('SELECT nodes.id, nodes.parent_id, types.name FROM nodes, types, closures WHERE nodes.id = closures.descendant_id AND closures.ancestor_id IN (SELECT consequent_id FROM rules WHERE name = %s) AND nodes.type_id = types.id ORDER BY parent_id ASC;', (self.uiRulesCombo.currentText(),))
            nodes = cur.fetchall()
            cur.close()
            for node in nodes:
                if node[0] != node[1]:
                    if (node[2] == 'variable'):
                        cur = self.conn.cursor()
                        cur.execute('SELECT variables.name FROM variables, nodes WHERE variables.id = nodes.variable_id AND nodes.id = %s;', (node[0],))
                        name = cur.fetchone()
                        cur.close()
                    elif (node[2] == 'hedge'):
                        cur = self.conn.cursor()
                        cur.execute('SELECT hedges.value FROM hedges, nodes WHERE hedges.id = nodes.hedge_id AND nodes.id = %s;', (node[0],))
                        name = cur.fetchone()
                        cur.close()
                    elif (node[2] == 'term'):
                        cur = self.conn.cursor()
                        cur.execute('SELECT terms.value FROM terms, nodes WHERE terms.id = nodes.term_id AND nodes.id = %s;', (node[0],))
                        name = cur.fetchone()
                        cur.close()
                    else:
                        name = node[2]
                    parents = self.uiConsequentTree.findItems('%s' % node[1], Qt.MatchExactly | Qt.MatchRecursive, 1)
                    item = QTreeWidgetItem()
                    item.setText(0, '%s' % name)
                    item.setText(1, '%s' % node[0])
                    parents[0].addChild(item)

        self.uiRenameRuleButton.setEnabled(True)
        self.uiDeleteRuleButton.setEnabled(True)
        self.uiAntecedentTree.setEnabled(True)
        self.uiConsequentTree.setEnabled(True)

    def onCreateRuleClicked(self):
        self.uiRulesCombo.setCurrentIndex(-1)
        self.uiRulesCombo.setEditable(True)
        self.uiRulesCombo.lineEdit().returnPressed.connect(self.onRuleEntered)
        self.uiRulesCombo.setFocus()
        self.uiCreateRuleButton.setEnabled(False)

    def onRuleEntered(self):
        self.uiRulesCombo.setEditable(False)
        self.uiCreateRuleButton.setEnabled(True)
        self.onRuleSelected()

    def onDeleteRuleClicked(self):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM rules WHERE name = %s;', (self.uiRulesCombo.currentText(),))
        self.conn.commit()
        cur.close()
        self.uiRulesCombo.removeItem(self.uiRulesCombo.currentIndex())

    def commitRule(self):
        self.uiCommitRuleButton.setEnabled(False)

    def onTabChanged(self):
        if (self.uiTabs.currentIndex() == 0):
            self.loadTerms()
            self.loadHedges()
            self.onVariableSelected()

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Window()
    widget.show()
    sys.exit(app.exec_())