# ===============================================================================
# Copyright 2015 Jake Ross
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
from traits.api import Str
from traitsui.api import View, UItem, EnumEditor
# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.pipeline.nodes.base import BaseNode
from pychron.processing.utils.grouping import group_analyses_by_key


class GroupingNode(BaseNode):
    # by_identifier = Bool
    # by_aliquot = Bool
    # by_sample = Bool
    by_key = Str
    keys = ('Aliquot', 'Identifier')
    analysis_kind = 'unknowns'
    name = 'Grouping'

    def configure(self):
        info = self.edit_traits()
        if info.result:
            return True

    def _generate_key(self):
        if self.by_key == 'Aliquot':
            key = lambda x: x.aliquot
        elif self.by_key == 'Identifier':
            key = lambda x: x.identifier
        return key

    def run(self, state):
        unks = getattr(state, self.analysis_kind)
        group_analyses_by_key(unks, key=self._generate_key())

    def traits_view(self):
        v = View(UItem('by_key',
                       style='custom',
                       editor=EnumEditor(name='keys')),
                 width=300,
                 title='Edit Grouping',
                 buttons=['OK', 'Cancel'],
                 kind='livemodal'
                 )
        return v

# ============= EOF =============================================
