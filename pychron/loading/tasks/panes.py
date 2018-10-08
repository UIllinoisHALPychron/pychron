# ===============================================================================
# Copyright 2013 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= enthought library imports =======================
from enable.component_editor import ComponentEditor
from pyface.tasks.traits_dock_pane import TraitsDockPane
from pyface.tasks.traits_task_pane import TraitsTaskPane
from traits.api import Int, Property
from traitsui.api import View, UItem, Item, VGroup, TabularEditor, HGroup, spring, EnumEditor, Tabbed
from traitsui.tabular_adapter import TabularAdapter

# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.envisage.icon_button_editor import icon_button_editor


class PositionsAdapter(TabularAdapter):
    columns = [('Identifier', 'identifier'),
               ('Irradiation', 'irradiation_str'),
               ('Sample', 'sample'),
               ('Material', 'material'),
               ('Position', 'position'),
               ('Weight', 'weight'),
               ('N. Xtals', 'nxtals'),
               ('Note', 'note')]


class GroupedPositionsAdapter(TabularAdapter):
    columns = [('Identifier', 'identifier'),
               ('Irradiation', 'irradiation_str'),
               ('Sample', 'sample'),
               ('Material', 'material'),
               ('Positions', 'position_str')]
    font = 'arial 10'
    identifier_width = Int(80)
    irradiation_str_width = Int(80)
    sample_width = Int(80)
    position_str_width = Int(80)

    def get_bg_color(self, obj, trait, row, column=0):
        item = getattr(obj, trait)[row]
        c = item.color
        if hasattr(c, '__iter__'):
            c = [x * 255 for x in c]
        return c

    def get_text_color(self, obj, trait, row, column=0):
        item = getattr(obj, trait)[row]
        color = 'black'
        if hasattr(item.color, '__iter__'):
            if sum(item.color[:3]) < 1.5:
                color = 'white'
        return color


class BaseLoadPane(TraitsDockPane):
    display_load_name = Property(depends_on='model.display_load_name')

    def _get_display_load_name(self):
        return '<font size=12 color="blue"><b>{}</b></font>'.format(self.model.display_load_name)


class LoadTablePane(BaseLoadPane):
    name = 'Positions'
    id = 'pychron.loading.positions'

    def traits_view(self):
        a = HGroup(Item('pane.display_load_name',
                        style='readonly',
                        label='Load'))

        b = UItem('positions',
                  editor=TabularEditor(adapter=PositionsAdapter(),
                                       # refresh='refresh_table',
                                       # scroll_to_row='scroll_to_row',
                                       # selected='selected_positions',
                                       multi_select=True))
        c = UItem('grouped_positions',
                  editor=TabularEditor(adapter=GroupedPositionsAdapter()))
        v = View(VGroup(a, Tabbed(b, c)))
        return v


class LoadPane(TraitsTaskPane):
    def traits_view(self):
        v = View(VGroup(UItem('canvas',
                              style='custom',
                              editor=ComponentEditor())))
        return v


class LoadDockPane(BaseLoadPane):
    name = 'Load'
    id = 'pychron.loading.load'

    def traits_view(self):
        a = HGroup(Item('pane.display_load_name', style='readonly', label='Load'),
                   spring,
                   # Item('group_positions',
                   #      label='Group Positions as Single Analysis',
                   #      tooltip='If this option is checked, all selected positions will '
                   #              'be treated as a single analysis',
                   #      visible_when='show_group_positions')
                   )
        b = UItem('canvas',
                  style='custom',
                  editor=ComponentEditor())
        v = View(VGroup(a, b))

        return v


class LoadControlPane(TraitsDockPane):
    name = 'Load'
    id = 'pychron.loading.controls'

    def traits_view(self):
        notegrp = VGroup(Item('retain_note',
                              tooltip='Retain the Note for the next hole',
                              label='Lock'),
                         Item('note', style='custom', show_label=False),
                         show_border=True,
                         label='Note')

        viewgrp = VGroup(HGroup(Item('use_cmap', label='Color Map'),
                                UItem('cmap_name', enabled_when='use_cmap')),
                         Item('show_hole_numbers'),
                         Item('show_identifiers'),
                         Item('show_weights'),
                         Item('show_nxtals'),
                         # Item('show_spans'),
                         show_border=True,
                         label='View')

        load_grp = VGroup(Item('username', editor=EnumEditor(name='available_user_names')),
                          HGroup(Item('load_name',
                                      editor=EnumEditor(name='loads'),
                                      label='Loads'),
                                 icon_button_editor('fetch_load_button', 'goo',
                                                    enabled_when='load_name',
                                                    tooltip='Fetch load from database'),
                                 icon_button_editor('add_button', 'add', tooltip='Add a load'),
                                 icon_button_editor('delete_button', 'delete', tooltip='Delete selected load'),
                                 icon_button_editor('archive_button', 'application-x-archive',
                                                    tooltip='Archive a set of loads')),
                          label='Load',
                          show_border=True)
        samplegrp = VGroup(HGroup(Item('irradiation', editor=EnumEditor(name='irradiations')),
                                  Item('level', editor=EnumEditor(name='levels'))),
                           Item('identifier', editor=EnumEditor(name='identifiers')),
                           Item('sample_info', style='readonly'),
                           Item('packet', style='readonly'),
                           HGroup(Item('weight', label='Weight (mg)'),
                                  Item('retain_weight', label='Lock',
                                       tooltip='Retain the Weight for the next hole')),
                           HGroup(Item('nxtals', label='N. Xtals'),
                                  Item('retain_nxtals', label='Lock',
                                       tooltip='Retain the N. Xtals for the next hole')),
                           HGroup(Item('npositions', label='NPositions'),
                                  Item('auto_increment')),
                           enabled_when='load_name',
                           show_border=True,
                           label='Sample')

        v = View(VGroup(load_grp,
                        samplegrp,
                        notegrp,
                        viewgrp))
        return v

# ============= EOF =============================================
