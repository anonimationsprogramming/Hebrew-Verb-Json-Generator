import sys
import json
from dataclasses import dataclass, field
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QGroupBox, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt

# ---------------- DATA ----------------

@dataclass
class Tense:
    forms: dict[str, str] = field(default_factory=dict)

@dataclass
class Hatya:
    present: Tense
    past: Tense
    future: Tense

@dataclass
class Binyan:
    translation: str
    conjugations: Hatya

@dataclass
class VerbRoot:
    letters: tuple[str, ...] = ()

@dataclass
class Verb:
    verb: str
    root: VerbRoot
    binyanim: dict[str, Binyan] = field(default_factory=dict)


# ---------------- GUI ----------------

class VerbApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("פעלים")

        # ---------------- SCROLL AREA SETUP ----------------
        main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)

        title = QLabel("פעלים")
        present = QLabel("הווה")
        past = QLabel("עבר")
        future = QLabel("עתיד")

        button = QPushButton("שמור")

        # ---------------- BASIC INFO ----------------
        form = QFormLayout()
        self.verb_input = QLineEdit()
        self.root_input = QLineEdit()
        self.binyan_input = QLineEdit()
        self.translation_input = QLineEdit()

        form.addRow("פועל", self.verb_input)
        form.addRow("שורש", self.root_input)
        form.addRow("בניין", self.binyan_input)
        form.addRow("תרגום", self.translation_input)


        # ---------------- TITLE ----------------
        layout.addWidget(title)


        # ---------------- FORM ----------------
        layout.addLayout(form)

        # ---------------- PRESENT ----------------
        layout.addWidget(present)
        self.present_fields = self.make_tense_fields(layout)

        # ---------------- PAST ----------------
        layout.addWidget(past)
        self.past_fields = self.make_tense_fields(layout)

        # ---------------- FUTURE ----------------
        layout.addWidget(future)
        self.future_fields = self.make_tense_fields(layout)

        # ---------------- SAVE BUTTON ----------------
        button.clicked.connect(self.save_verb)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

        # attach container to scroll area
        scroll.setWidget(container)

        # Add styles        
        self.setStyleSheet("QWidget {border: 1px solid black; border-radius: 20; font-family:serif; font-size: 40px; background-color: white; color: black;} ")
        title.setStyleSheet("QLabel{font-family:serif; font-size: 60px; color: black; font-weight: bold;} ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button.setStyleSheet("QPushButton{font-family:serif; font-size: 40px; background-color: black; color: white; font-weight: bold; min-width: 100px; max-width: 100px;} ")
        present.setStyleSheet("QLabel{font-family:serif; font-size: 45px; color: black; font-weight: bold;} ")
        past.setStyleSheet("QLabel{font-family:serif; font-size: 45px; color: black; font-weight: bold;} ")
        future.setStyleSheet("QLabel{font-family:serif; font-size: 45px; color: black; font-weight: bold;} ")



        # add scroll to window
        main_layout.addWidget(scroll)

    def make_tense_fields(self, layout):
        people = ["אני", "אתה", "את", "הוא", "היא", "אנחנו", "אתם", "אתן", "הם", "הן"]

        group = {}
        grid = QGridLayout()

        for i, person in enumerate(people):
            label = QLabel(person)
            field = QLineEdit()

            grid.addWidget(label, i, 0)
            grid.addWidget(field, i, 1)

            group[person] = field

        layout.addLayout(grid)
        return group

    def collect_tense(self, fields):
        return Tense({k: v.text() for k, v in fields.items()})

    def save_verb(self):
        verb = Verb(
            verb=self.verb_input.text(),
            root=VerbRoot(tuple(self.root_input.text().split())),
            binyanim={
                self.binyan_input.text(): Binyan(
                    translation=self.translation_input.text(),
                    conjugations=Hatya(
                        present=self.collect_tense(self.present_fields),
                        past=self.collect_tense(self.past_fields),
                        future=self.collect_tense(self.future_fields)
                    )
                )
            }
        )


        FILE = "verbs.json"

        try:
            with open(FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        data.append({
            "פועל": verb.verb,
            "שורש": list(verb.root.letters),
            "בניין": {
                k: {
                    "תרגום": v.translation,
                    "הטיה": {
                        "הווה": v.conjugations.present.forms,
                        "עבר": v.conjugations.past.forms,
                        "עתיד": v.conjugations.future.forms,
                    }
                }
                for k, v in verb.binyanim.items()
            }
        })

        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print("Saved ✔")

# ---------------- RUN ----------------

app = QApplication(sys.argv)
app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
window = VerbApp()
window.show()
sys.exit(app.exec())