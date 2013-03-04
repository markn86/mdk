#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Moodle Development Kit

Copyright (c) 2013 Frédéric Massart - FMCorz.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

http://github.com/FMCorz/mdk
"""

import sys
from lib.command import Command
from lib.tools import debug


class UpgradeCommand(Command):

    _arguments = [
        (
            ['-a', '--all'],
            {
                'action': 'store_true',
                'dest': 'all',
                'help': 'upgrade each instance'
            }
        ),
        (
            ['-i', '--integration'],
            {
                'action': 'store_true',
                'dest': 'integration',
                'help': 'upgrade integration instances'
            }
        ),
        (
            ['-s', '--stable'],
            {
                'action': 'store_true',
                'dest': 'stable',
                'help': 'upgrade stable instances'
            }
        ),
        (
            ['-n', '--no-checkout'],
            {
                'action': 'store_true',
                'dest': 'nocheckout',
                'help': 'do not checkout the stable branch before upgrading'
            }
        ),
        (
            ['-u', '--update'],
            {
                'action': 'store_true',
                'dest': 'update',
                'help': 'update the instance before running the upgrade script'
            }
        ),
        (
            ['names'],
            {
                'default': None,
                'help': 'name of the instances',
                'metavar': 'names',
                'nargs': '*'
            }
        )
    ]
    _description = 'Run the Moodle upgrade script'

    def run(self, args):

        names = args.names
        if args.all:
            names = self.Wp.list()
        elif args.integration or args.stable:
            names = self.Wp.list(integration=args.integration, stable=args.stable)

        Mlist = self.Wp.resolveMultiple(names)
        if len(Mlist) < 1:
            raise Exception('No instances to work on. Exiting...')

        errors = []

        for M in Mlist:
            if args.update:
                debug('Updating %s...' % M.get('identifier'))
                try:
                    M.update()
                except Exception as e:
                    errors.append(M)
                    debug('Error during update. Skipping...')
                    debug(e)
                    continue
            debug('Upgrading %s...' % M.get('identifier'))

            try:
                M.upgrade(args.nocheckout)
            except Exception as e:
                errors.append(M)
                debug('Error during the upgrade of %s' % M.get('identifier'))
                debug(e)
            debug('')
        debug('Done.')

        if errors and len(Mlist) > 1:
            debug('')
            debug('/!\ Some errors occurred on the following instances:')
            for M in errors:
                debug('- %s' % M.get('identifier'))
            # TODO Do not use sys.exit() but handle error code
            sys.exit(1)
