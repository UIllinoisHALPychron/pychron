#===============================================================================
# Copyright 2013 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
import os
from traits.api import HasTraits, Any, List, Date, Str, Long, \
    Float, Button, Int, Instance, on_trait_change
from traitsui.api import View, Item, EnumEditor, HGroup, spring, \
    UItem, VGroup, TabularEditor, InstanceEditor

#============= standard library imports ========================
#============= local library imports  ==========================
from traitsui.tabular_adapter import TabularAdapter
import yaml
from pychron.database.records.isotope_record import IsotopeRecordView
from pychron.envisage.tasks.base_editor import BaseTraitsEditor
from pychron.envisage.tasks.pane_helpers import icon_button_editor
from pychron.pdf.options import PDFTableOptions
from pychron.processing.tables.summary_table_pdf_writer import SummaryTablePDFWriter
from pychron.processing.tasks.browser.panes import AnalysisAdapter
from pychron.ui.custom_label_editor import CustomLabel


class InterpretedAge(HasTraits):
    create_date = Date
    id = Long

    sample = Str
    identifier = Str
    material = Str
    irradiation = Str

    age = Float
    age_err = Float
    wtd_kca = Float
    wtd_kca_err = Float

    age_kind = Str
    mswd = Float
    nanalyses = Int

    def traits_view(self):
        return View(HGroup(Item('age_kind', style='readonly', show_label=False),
                           Item('age', style='readonly'),
                           Item('age_err', style='readonly')))


class InterpretedAgeAdapter(TabularAdapter):
    columns = [('Sample', 'sample'),
               ('Identifier', 'identifier'),
               ('Kind', 'kind'),
               ('Age', 'age'),
               ('Error', 'age_err'),
               ('NAnalyses', 'nanalyses'),
               ('MSWD', 'mswd')]

    font = 'arial 10'




class InterpretedAgeEditor(BaseTraitsEditor):
    selected_history = Any
    selected_history_name = Str
    selected_identifier = Str

    histories = List
    history_names = List
    analyses = List
    processor = Any

    append_button = Button
    replace_button = Button
    interpreted_ages = List

    pdf_table_options=Instance(PDFTableOptions, ())

    def open_table_recipe(self, p):
        self._open_recipe_file(p)

    def save_pdf_tables(self, p):
        self.save_summary_table(p)

    def save_summary_table(self, p):
        w = SummaryTablePDFWriter()
        items = self.interpreted_ages
        title = self.get_title()

        opt=self.pdf_table_options
        # w.use_alternating_background=opt.use_alternating_background
        w.options=opt
        w.build(p, items, title)

        self._save_recipe_file(p)

    def get_title(self):
        opt=self.pdf_table_options
        if opt.auto_title:
            title=self._generate_title()
        else:
            title=opt.title
        return title

    def set_samples(self, samples):
        self.analyses = []
        self.selected_history_name = ''
        self.selected_history = InterpretedAge()

        if samples:
            lns = [si.labnumber for si in samples]
            db = self.processor.db
            with db.session_ctx():
                histories = db.get_interpreted_age_histories(lns)

                self.histories = [self._interpreted_age_factory(db, hi) for hi in histories]

                self.history_names = [hi.name for hi in self.histories]
                if self.history_names:
                    self.selected_history_name = self.history_names[-1]

    def _save_recipe_file(self, p):
        head, ext=os.path.splitext(p)
        p='{}.{}'.format(head, 'yaml')

        #assemble recipe
        d={'title':str(self.get_title()),
           'options':self.pdf_table_options.dump_yaml(),
           'ids':[int(ia.id) for ia in self.interpreted_ages]}

        with open(p, 'w') as fp:
            yaml.dump(d, fp)

    def _open_recipe_file(self, p):
        with open(p, 'r') as fp:
            d=yaml.load(fp)

        db=self.processor.db
        with db.session_ctx():
            ias=[]
            for hid in d['ids']:
                hist=db.get_interpreted_age_history(hid)
                ias.append(self._interpreted_age_factory(db, hist))

        self.interpreted_ages=ias

        self.pdf_table_options.load_yaml(d['options'])
        # self.pdf_table_options.trait_set(**d['options'])

    def _generate_title(self):
        return 'Table 1. Ar/Ar Summary Table'

    def _interpreted_age_factory(self, db, hi):
        dbln = db.get_labnumber(hi.identifier)
        sample = None
        irrad = None
        material = None
        if dbln:
            if dbln.sample:
                sample = dbln.sample.name
                dbmat = dbln.sample.material
                if dbmat:
                    material = dbmat.name

            pos = dbln.irradiation_position
            if pos:
                level = pos.level
                irrad = level.irradiation
                irrad = '{}{} {}'.format(irrad.name, level.name, pos.position)
        ia=hi.interpreted_age
        n = len(ia.sets)
        it = InterpretedAge(create_date=hi.create_date,
                            id=hi.id,
                            age=ia.age,
                            age_err=ia.age_err,
                            wtd_kca=ia.wtd_kca or 0,
                            wtd_kca_err=ia.wtd_kca_err or 0,
                            mswd=ia.mswd,
                            kind=ia.age_kind,
                            identifier=hi.identifier,
                            sample=sample or '',
                            irradiation=irrad or '',
                            material=material or '',
                            nanalyses=n,
                            name='{} - {}'.format(hi.create_date, ia.age_kind))

        return it

    @on_trait_change('interpreted_ages[]')
    def _interpreted_ages_changed(self):
        self.pdf_table_options.title=self._generate_title()

    def _selected_history_name_changed(self):
        if self.selected_history_name:
            def func(a):
                ir = IsotopeRecordView()
                ir.create(a)
                return ir

            db = self.processor.db

            hist = next((hi for hi in self.histories if hi.name == self.selected_history_name), None)
            self.selected_history = hist
            self.selected_identifier = '{} {}'.format(hist.sample, hist.identifier)

            with db.session_ctx():
                dbhist = db.get_interpreted_age_history(hist.id)
                s = dbhist.interpreted_age.sets

                self.analyses = [func(a.analysis) for a in s]

    def _append_button_fired(self):
        self.interpreted_ages.append(self.selected_history)

    def _replace_button_fired(self):
        self.interpreted_ages = [self.selected_history]

    def traits_view(self):
        histories_grp = HGroup(icon_button_editor('append_button', 'add'),
                               icon_button_editor('replace_button', 'arrow_refresh'),
                               spring,
                               CustomLabel('selected_identifier'),
                               spring, UItem('selected_history_name', editor=EnumEditor(name='history_names')))
        analyses_grp = UItem('analyses', editor=TabularEditor(adapter=AnalysisAdapter()))
        selected_grp = UItem('selected_history', style='custom', editor=InstanceEditor())

        interpreted_grp = UItem('interpreted_ages',
                                editor=TabularEditor(adapter=InterpretedAgeAdapter(),
                                                     operations=['move','delete'],
                                                     ))
        options_grp=UItem('pdf_table_options', style='custom')

        v = View(VGroup(histories_grp,
                        selected_grp,
                        analyses_grp,
                        options_grp,
                        interpreted_grp))
        return v

#============= EOF =============================================

