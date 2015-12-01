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
from traits.api import Int

# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.hardware.core.abstract_device import AbstractDevice


class NMGRLFunnel(AbstractDevice):
    down_position = Int
    up_position = Int

    def load_additional_args(self, config):
        self.set_attribute(config, 'down_position', 'Positioning', 'down_position', cast='int')
        self.set_attribute(config, 'up_position', 'Positioning', 'up_position', cast='int')

# ============= EOF =============================================