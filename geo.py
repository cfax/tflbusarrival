import numpy as np
import re
import os
from flask import url_for


class PostcodeError(Exception):
    """Base class of postcode-related errors"""
    pass


class PostcodeNotFoundError(PostcodeError):
    """Cannot find the postcode in any file."""
    pass


class PostcodeMalformedError(PostcodeError):
    """The postcode is not valid."""
    pass


class Geo(object):

    def __init__(self, postcode):
        """Initialize the object with the specified postcode"""
        self.postcode_dir = '.' + url_for('static', filename='postcodes')
        # Postcode regex. Notice we don't care about the Girobank's postcode.
        self.postcode_re = re.compile('(([A-PR-UWYZ][0-9][0-9]?)|' +                    # outward code
                                      '(([A-PR-UWYZ][A-HK-Z][0-9][0-9]?)|' +            #
                                      '(([A-PR-UWYZ][0-9][A-HJKPSTUW])|' +              #
                                      '([A-PR-UWYZ][A-HK-Z][0-9][ABEHMNPRVWXY]))))' +   # end of outward code
                                      '[0-9][ABD-HJLNP-UW-Z]{2}$')                      # inward code

        # Validate postcode
        postcode = self.postcode_re.match(postcode.replace(' ', '').upper())
        if not postcode:
            raise PostcodeMalformedError
        self.postcode = postcode.group()

    def deg2rad(self, d):
        """Convert d degrees in radians"""
        return np.pi*d/180

    def rad2deg(self, r):
        """Convert r radians in degrees"""
        return 180.*r/np.pi

    def getLatitudeAndLongitude(self):
        """Convert Easting and Northing in latitude and longitude
        Source: http://www.ordnancesurvey.co.uk/docs/support/guide-coordinate-systems-great-britain.pdf
        """
        E, N = self.getEastingAndNorthing()
        # Ellipsoid: Airy 1830
        a = 6377563.396  # semi-major axis [m]
        b = 6356256.909  # semi-minor axis [m]
        e2 = (a**2 - b**2)/(a**2)  # ellipsoid squared eccentricity
        n = (a-b) / (a+b)

        phi_0 = self.deg2rad(49.)  # latitude of true origin [radians N]
        lam_0 = self.deg2rad(-2.)  # longitude of true origin [radians E]
        F_0 = 0.9996012717  # scale factor on central meridian
        E_0 = 400000.   # easting of true origin [m]
        N_0 = -100000.  # northing of true origin [m]

        def compute_M(phi):
            return b*F_0*(
                (1 + n + 5./4 * n**2 + 5./4 * n**3) * (phi-phi_0) - \
                (3 * n + 3 * n**2 + 21./8 * n**3) * np.math.sin(phi-phi_0) * np.math.cos(phi+phi_0) + \
                (15./8 * n**2 + 15./8 * n**3) * np.math.sin(2*(phi-phi_0)) * np.math.cos(2*(phi+phi_0)) - \
                35./24 * n**3 * np.math.sin(3*(phi-phi_0)) * np.math.cos(3*(phi+phi_0))
            )

        phi = (N-N_0)/(a*F_0) + phi_0
        M = compute_M(phi)

        while N - N_0 - M >= 0.00001:  # [m]
            phi = ((N - N_0 - M) / (a*F_0)) + phi
            M = compute_M(phi)

        nu = a*F_0 * ((1 - e2 * (np.math.sin(phi))**2)**(-0.5))
        rho = a*F_0 * (1 - e2) * (1 - e2 * (np.math.sin(phi))**2)**(-1.5)
        eta2 = nu/rho - 1

        vii = np.math.tan(phi) / (2*rho*nu)
        viii = np.math.tan(phi) / (24*rho*nu**3) * \
               (5 + 3*(np.math.tan(phi))**2 + eta2 - 9*eta2*(np.math.tan(phi))**2)
        ix = np.math.tan(phi) / (720*rho*nu**5) * \
             (61 + 90*(np.math.tan(phi))**2 + 45*(np.math.tan(phi))**4)
        x = (1./np.math.cos(phi)) / nu
        xi = (1./np.math.cos(phi)) / (6*nu**3) * (nu/rho + 2*(np.math.tan(phi))**2)
        xii = (1./np.math.cos(phi)) / (120*nu**5) * \
              (5 + 28*(np.math.tan(phi))**2 + 24*(np.math.tan(phi))**4)
        xiia = (1./np.math.cos(phi)) / (5040*nu**7) * \
               (61 + 662*(np.math.tan(phi))**2 + 1320*(np.math.tan(phi))**4 + 720*(np.math.tan(phi))**6)

        phi = phi - vii*(E-E_0)**2 + viii*(E-E_0)**4 - ix*(E-E_0)**6
        lam = lam_0 + x*(E-E_0) - xi*(E-E_0)**3 + xii*(E-E_0)**5 - xiia*(E-E_0)**7

        return self.rad2deg(phi), self.rad2deg(lam)

    def getEastingAndNorthing(self):
        """Return easting and northing for this postcode.

        :return: easting and northing
        """

        # Validate postcode
        prefix = re.match('([A-Z]{1,2})[0-9]', self.postcode)

        for line in open(os.path.join(self.postcode_dir, prefix.group(1).lower() + '.csv')):
            full_postcode, remainder = line.split(',', 1)
            if full_postcode.strip('"').replace(' ', '') == self.postcode:
                break
        else:
            raise PostcodeNotFoundError

        _, easting, northing, _ = remainder.split(',', 3)
        return float(easting), float(northing)
