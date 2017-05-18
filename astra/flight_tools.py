# coding=utf-8

"""
flight_tools.py
ASTRA High Altitude Balloon Flight Planner

DESCRIPTION
--------------

Flight Tools
A collection of small flight-specific tools used throughout the simulation.
These tools generally perform basic performance calculations, such as balloon diameter and drag.


USAGE
--------------

Note: a flight_tools object needs to be instantiated to be able to use all the following methods!

The methods available are:

    liftingGasMass(nozzleLift,balloonMass,ambientTempC,ambientPressMbar,gasMolecularMass,excessPressureCoefficient)
        This method calculates the gas mass, the balloon volume and the balloon diameter.
        Returns a list of three float variables: [gas_mass, balloon_volume, balloon_diameter]

        Parameters' units:
            nozzleLift: kg
            balloonMass: kg
            ambientTempC: Celsius
            ambientPressMbar: millibar
            gasMolecularMass: kg/mol
            excessPressCoefficient: dimension-less

    gasMassForFloat(currentAltitude,floatingAltitude,gasMassAtInflation,gasMassAtFloatingAltitude,ventStart=500)
        This method should only be used for floating flights. It returns the gas mass profile to simulate the valves
        venting air to reach floating conditions.
        Returns a float with the gas mass at the currentAltitude.

        Parameters:
            currentAltitude: the altitude for which the gas mass is required [m]
            floatingAltitude: the target altitude for float [m]
            gasMassAtInflation: the initial gas mass, before venting [kg]
            gasMassAtFloatingAltitude: the final gas mass required to reach floating conditions [kg]
            ventStart: how many meters below the target floating altitude should the venting start. Default is 500m

    nozzleLiftForFloat(nozzleLiftAtInflation,airDensity,gasDensity,balloonVolume,balloonMass,currentAltitude,floatingAltitude,ventStart=500)
        This method should only be used for floating flights. It returns the nozzle lift of a balloon in floating
        configuration. Below the venting threshold (floatingAltitude-ventStart), the nozzle lift is unchanged.
        Otherwise, it's recalculated.
        Returns a float with the nozzle lift [kg].

        Parameters:
            nozzleLiftAtInflation: nozzle lift of the balloon at inflation [kg]
            airDensity: density of air at current altitude [kg/m3]
            gasDensity: density of the gas at current altitude [kg/m3]
            balloonVolume: volume of the balloon at current altitude [m3]
            balloonMass: total balloon mass at current altitude [kg]
            currentAltitude: altitude at which the nozzle lift is required [m]
            floatingAltitude: target altitude for floating conditions [m]
            ventStart: how many meters below the target floating altitude should the venting start. Default is 500m

    balloonDrag(diameter,ascentRate,density,viscosity)
        This method calculates the balloon drag.
        Returns a float with the balloon drag in [N].

        Parameters:
            diameter: balloon diameter [m]
            ascentRate: balloon vertical velocity [m/s]
            density: current air density [kg/m3]
            viscosity: current air viscosity [kg/m3]

    parachuteDrag(descentRate, density)
        This method calculates the drag generated by the parachute on descent.
        Returns a float with the parachute drag in [N].

        Parameters:
            descentRate: balloon vertical velocity [m/s]
            density: current air density [kg/m3]


University of Southampton
Niccolo' Zapponi, nz1g10@soton.ac.uk, 22/04/2013
"""

__author__ = "Niccolo' Zapponi, University of Southampton, nz1g10@soton.ac.uk"

from math import pi


class flight_tools:
    """
    Flight Tools
    A collection of small flight-specific tools used throughout the simulation.
    These tools generally perform basic performance calculations, such as balloon diameter and drag.
    """

    # Constants

    R = 8.31447 # m^3Pa/mol K
    airMolecularMass = 0.02896 # kg/mol
    HeMolecularMass = 0.004002602 # kg/mol
    HydrogenMolecularMass = 0.0020159 # kg/mol

    highCD = 0.0
    lowCD = 0.0
    transition = 0.0
    ReBand = 0.0

    parachuteAref = 0
    parachuteCD = 0.0


    def liftingGasMass(self, nozzleLift, balloonMass, ambientTempC, ambientPressMbar, gasMolecularMass,
                       excessPressureCoefficient):
        """
        liftingGasMass(nozzleLift,balloonMass,ambientTempC,ambientPressMbar,gasMolecularMass,excessPressureCoefficient)
            This method calculates the gas mass, the balloon volume and the balloon diameter.

            Returns a list of three float variables: [gas_mass, balloon_volume, balloon_diameter]

            Parameters' units:
                nozzleLift: kg
                balloonMass: kg
                ambientTempC: Celsius
                ambientPressMbar: millibar
                gasMolecularMass: kg/mol
                excessPressCoefficient: dimension-less
        """

        gasDensity = excessPressureCoefficient * ambientPressMbar * 100 * gasMolecularMass / (
            self.R * (ambientTempC + 273.15))
        airDensity = ambientPressMbar * 100 * self.airMolecularMass / (self.R * (ambientTempC + 273.15))

        balloonVolume = (nozzleLift + balloonMass) / (airDensity - gasDensity)
        gasMass = balloonVolume * gasDensity
        balloonDiameter = (6. * balloonVolume / pi) ** (1. / 3)

        return [gasMass, balloonVolume, balloonDiameter]


    def gasMassForFloat(self, currentAltitude, floatingAltitude, gasMassAtInflation, gasMassAtFloatingAltitude,
                        ventStart=500):
        """
        gasMassForFloat(currentAltitude,floatingAltitude,gasMassAtInflation,gasMassAtFloatingAltitude,ventStart=500)
            This method should only be used for floating flights. It returns the gas mass profile to simulate the valves
            venting air to reach floating conditions.

            Returns a float with the gas mass at the currentAltitude.

            Parameters:
                currentAltitude: the altitude for which the gas mass is required [m]
                floatingAltitude: the target altitude for float [m]
                gasMassAtInflation: the initial gas mass, before venting [kg]
                gasMassAtFloatingAltitude: the final gas mass required to reach floating conditions [kg]
                ventStart: how many meters below the target floating altitude should the venting start. Default is 500m
        """

        if currentAltitude < (floatingAltitude - ventStart):
            # Below the threshold to start venting. The gas mass is unchanged
            return gasMassAtInflation
        elif currentAltitude < floatingAltitude:
            # The balloon is approaching the target altitude, start venting

            # The following is the equation for linear interpolation between the start and the end of the venting.
            return (gasMassAtInflation - gasMassAtFloatingAltitude) / float(ventStart) * (
                floatingAltitude - currentAltitude) + gasMassAtFloatingAltitude
        else:
            # The balloon has reached the floating altitude
            return gasMassAtFloatingAltitude


    def nozzleLiftForFloat(self, nozzleLiftAtInflation, airDensity, gasDensity, balloonVolume, balloonMass,
                           currentAltitude, floatingAltitude, ventStart=500):
        """
        nozzleLiftForFloat(nozzleLiftAtInflation,airDensity,gasDensity,balloonVolume,balloonMass,currentAltitude,floatingAltitude,ventStart=500)
            This method should only be used for floating flights. It returns the nozzle lift of a balloon in floating
            configuration. Below the venting threshold (floatingAltitude-ventStart), the nozzle lift is unchanged.
            Otherwise, it's recalculated.

            Returns a float with the nozzle lift [kg].

            Parameters:
                nozzleLiftAtInflation: nozzle lift of the balloon at inflation [kg]
                airDensity: density of air at current altitude [kg/m3]
                gasDensity: density of the gas at current altitude [kg/m3]
                balloonVolume: volume of the balloon at current altitude [m3]
                balloonMass: total balloon mass at current altitude [kg]
                currentAltitude: altitude at which the nozzle lift is required [m]
                floatingAltitude: target altitude for floating conditions [m]
                ventStart: how many meters below the target floating altitude should the venting start. Default is 500m
        """

        if currentAltitude < (floatingAltitude - ventStart):
            # Below the threshold to start venting. The nozzle lift is unchanged.
            return nozzleLiftAtInflation
        else:
            # The balloon has started venting gas, nozzle lift needs to be recalculated.
            currentNozzleLift = (airDensity - gasDensity) * balloonVolume - balloonMass

            return currentNozzleLift


    def balloonDrag(self, diameter, ascentRate, density, viscosity):
        """
        balloonDrag(diameter,ascentRate,density,viscosity)
            This method calculates the balloon drag.

            Returns a float with the balloon drag in [N].

            Parameters:
                diameter: balloon diameter [m]
                ascent rate: balloon vertical velocity [m/s]
                density: current air density [kg/m3]
                viscosity: current air viscosity [kg/m3]
        """

        reynoldsNumber = density * abs(ascentRate) * diameter / viscosity

        # Balloon CD
        if reynoldsNumber < self.transition * 1e5:
            balloonCD = self.highCD
        elif reynoldsNumber < (self.transition + self.ReBand) * 1e5:
            balloonCD = self.highCD - (self.highCD - self.lowCD) * (
                (reynoldsNumber - self.transition * 1e5) / (self.ReBand * 1e5) )
        else:
            balloonCD = self.lowCD

        return 0.5 * density * (abs(ascentRate) ** 2) * (pi * (diameter ** 2) / 4) * balloonCD


    def parachuteDrag(self, descentRate, density):
        """
        parachuteDrag(descentRate, density)
            This method calculates the drag generated by the parachute on descent.

            Returns a float with the parachute drag in [N].

            Parameters:
                descentRate: balloon vertical velocity [m/s]
                density: current air density [kg/m3]
        """


        return 0.5 * density * descentRate ** 2 * self.parachuteAref * self.parachuteCD