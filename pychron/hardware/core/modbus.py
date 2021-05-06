# ===============================================================================
# Copyright 2021 ross
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

class ModbusMixin:
    """
    simple mapper of the Modbus commands
    """

    def _func(self, funcname, *args, **kw):
        if self.communicator:
            return getattr(self.communicator, funcname)(*args, **kw)

    def _read_coils(self, *args, **kw):
        return self._func('read_coils', *args, **kw)

    def _write_coil(self, *args, **kw):
        return self._func('write_coils', *args, **kw)

    def _read_holding_registers(self, *args, **kw):
        return self._func('read_holding_registers', *args, **kw)

    def _read_input_registers(self, *args, **kw):
        return self._func('read_input_registers', *args, **kw)

    def _write_register(self, *args, **kw):
        return self._func('write_register', *args, **kw)

    def _write_registers(self, *args, **kw):
        return self._func('write_registers', *args, **kw)

# ============= EOF =============================================