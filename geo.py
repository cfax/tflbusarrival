import numpy as np
import re
import os
from flask import url_for

class Geo(object):

    def __init__(self):
        self.postcode_dir = os.path.join(url_for('static', filename='postcodes'))

    def deg2rad(self, d):
        """Convert d degrees in radians"""
        return np.pi*d/180

    def rad2deg(self, r):
        """Convert r radians in degrees"""
        return 180.*r/np.pi

    def getLatitudeAndLongitude(self, E, N):
        """Convert Easting and Northing in latitude and longitude
        Source: http://www.ordnancesurvey.co.uk/docs/support/guide-coordinate-systems-great-britain.pdf
        """
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

    def getEastingAndNorthing(self, postcode):
        """Given a postcode, return northing and easting"""
        postcode = postcode.upper()
        prefix = re.match('[a-z]{1,2}', postcode.lower)
        if not prefix:
            raise LookupError  # TODO: create own error

        for line in open(os.path.join(self.postcode_dir, prefix.group() + '.csv')):
            full_postcode, remainder = line.split(',', 1)
            if full_postcode.strip('"') == postcode:
                break
        else:
            raise Exception # TODO create own error

        _, easting, northing, _ = remainder.split(',', 4)
        return easting, northing
