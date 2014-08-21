import re

__all__ = ['PhysicalConstants', 'SpeciesIdentifier']


class PhysicalConstants:
    """
    gives you some constants.
    """
    import numpy as np

    c = 299792458.0
    me = 9.109383e-31
    mass_u = me * 1836.2
    qe = 1.602176565e-19
    mu0 = np.pi * 4e-7  # N/A^2
    epsilon0 = 1 / (mu0 * c ** 2)  # 8.85419e-12 As/Vm

    @staticmethod
    def ncrit_um(lambda_um):
        '''
        Critical plasma density in particles per m^3 for a given
        wavelength lambda_um in microns.
        '''
        return 1.11e27 * 1 / (lambda_um ** 2)  # 1/m^3

    @staticmethod
    def ncrit(laslambda):
        '''
        Critical plasma density in particles per m^3 for a given
        wavelength laslambda in m.
        '''
        return PhysicalConstants.ncrit_um(laslambda * 1e6)  # 1/m^3


class SpeciesIdentifier(PhysicalConstants):
    '''
    This Class provides static methods for deriving particle properties
    from species Names. The only reason for this to be a class is that it
    can be used as a mixin.
    '''

    # unit: electronmass
    _masslist = {'electrongold': 1, 'proton': 1836.2 * 1,
                 'ionp': 1836.2, 'ion': 1836.2 * 12, 'c6': 1836.2 * 12,
                 'ionf': 1836.2 * 19, 'Palladium': 1836.2 * 106,
                 'Palladium1': 1836.2 * 106, 'Palladium2': 1836.2 * 106,
                 'Ion': 1836.2, 'Photon': 0, 'Positron': 1, 'positron': 1,
                 'gold1': 1836.2 * 197, 'gold2': 1836.2 * 197,
                 'gold3': 1836.2 * 197, 'gold4': 1836.2 * 197,
                 'gold7': 1836.2 * 197, 'gold10': 1836.2 * 197,
                 'gold20': 1836.2 * 197}

    # unit: elementary charge
    _chargelist = {'electrongold': -1, 'proton': 1,
                   'ionp': 1, 'ion': 1, 'c6': 6,
                   'ionf': 1, 'Palladium': 0,
                   'Palladium1': 1, 'Palladium2': 2,
                   'Ion': 1, 'Photon': 0, 'Positron': 1, 'positron': 1,
                   'gold1': 1, 'gold2': 2, 'gold3': 3,
                   'gold4': 4, 'gold7': 7, 'gold10': 10,
                   'gold20': 20}

    _isionlist = {'electrongold': False, 'proton': True,
                  'ionp': True, 'ion': True, 'c6': True,
                  'ionf': True, 'f9': True, 'Palladium': True,
                  'Palladium1': True, 'Palladium2': True,
                  'Ion': True, 'Photon': False, 'Positron': False,
                  'positron': False,
                  'gold1': True, 'gold2': True, 'gold3': True,
                  'gold4': True, 'gold7': True, 'gold10': True,
                  'gold20': True}

    #  unit: amu
    _masslistelement = {'H': 1, 'He': 4, 'C': 12, 'N': 14, 'O': 16, 'F': 19,
                        'Ne': 20.2, 'Al': 27, 'Si': 28, 'Ar': 40, 'Au': 197}

    @staticmethod
    def isejected(species):
        s = species.replace('/', '')
        r = re.match(r'(ejected_)(.*)', s)
        return r is not None

    @classmethod
    def identifyspecies(cls, species):
        """
        Returns a dictionary contining particle informations.
        The following keys in the dictionary will always be present:
        name   species name string
        mass    kg (SI)
        charge  C (SI)
        tracer  boolean
        ejected boolean

        Valid Examples:
        Periodic Table symbol + charge state: c6, F2, H1, C6b
        ionm#c# defining mass and charge:  ionm12c2, ionc20m110
        advanced examples:
        ejected_tracer_ionc5m20b, ejected_tracer_electronx,
        ejected_c6b, tracer_proton, protonb
        """
        ret = {'tracer': False, 'ejected': False, 'name': species}
        s = species.replace('/', '')

        # Regex for parsing ion species name.
        # See docsting for valid examples
        regex = '(?P<prae>(.*_)*)(?P<name>(ionc(?P<c1>\d+)m(?P<m2>\d+)|' \
                'ionm(?P<m1>\d+)c(?P<c2>\d+))|(?P<electron>[Ee]le[ck]tron)|' \
                '(?P<elem>[A-Za-z]+)(?P<elem_c>\d*))(?P<suffix>[a-z]*)'
        r = re.match(regex, s)
        if r is None:
            raise Exception('Species ' + str(s) +
                            ' does not match regex name pattern: ' +
                            str(regex))
        regexdict = r.groupdict()

        # recognize anz prae and add dictionary key
        if regexdict['prae']:
            for i in regexdict['prae'].split('_'):
                key = i.replace('_', '')
                if not key == '':
                    ret[key] = True

        # Name Element + charge state: C1, C6, F2, F9, Au20, Pb34a
        if regexdict['elem']:
            try:
                ret['mass'] = float(cls._masslistelement[regexdict['elem']]) * \
                    1836.2 * cls.me
                ret['charge'] = float(regexdict['elem_c']) * cls.qe
                ret['ision'] = True
            except KeyError:
                # this pattern will also match, if name is defined in masslist,
                # so just ignore if key is not found.
                pass

        if regexdict['electron']:
            ret['mass'] = cls.me
            ret['charge'] = -1 * cls.qe
            ret['ision'] = False

        if regexdict['c1']:
            ret['mass'] = float(regexdict['m2']) * 1836.2 * cls.me
            ret['charge'] = float(regexdict['c1']) * cls.qe
            ret['ision'] = True

        if regexdict['c2']:
            ret['mass'] = float(regexdict['m1']) * 1836.2 * cls.me
            ret['charge'] = float(regexdict['c2']) * cls.qe
            ret['ision'] = True

        # simply added to _masslist and _chargelist
        # this should not be used anymore
        if regexdict['name'] in cls._masslist:
            ret['mass'] = float(cls._masslist[regexdict['name']]) * cls.me
        if regexdict['name'] in cls._chargelist:
            ret['charge'] = float(cls._chargelist[regexdict['name']] * cls.qe)
        if regexdict['name'] in cls._isionlist:
            ret['ision'] = cls._isionlist[regexdict['name']]

        if not (('mass' in ret) and ('charge' in ret) and ('ision' in ret)):
            raise Error('species ' + species + ' not recognized.')

        return ret







