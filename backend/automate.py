# KLassen aendern sich wahrscheinlich nochmal, aber wenn ihr mir die
# funktionalitaet stellt, aender ich das mir selber <3
# pass als keyword macht nichts ausser meinen typesetter happy


class WebotConfig():
    """NO need fuer aktion, fuell ich selber."""
    def __init__(self):
        pass


class WebotCtrl():
    def __init__(self):
        self.sock = None
        self.config = WebotConfig()

    def init(self):
        # nothing to do here
        self.start_program()
        self.establish_connection()

    def close(self):
        # nothing to do here
        self.close_connection()
        self.close_program()

    def is_program_started(self):
        # laesst es sich ueberpruefen ob webot gestartet ist?
        pass

    def start_program(self):
        if self.is_program_started() is False:
            # hier programm starten
            pass

    def close_program(self):
        if self.is_program_started() is True:
            # hier programm schliessen
            pass

    def establish_connection(self):
        # start tcp connection to Webot
        # self.sock = ...
        pass

    def close_connection(self):
        # close tcp connection to Webot
        pass

    def start_env(self, seed=1, simulations_speed=1, num_obstacles=1):
        # environment mit den settings ueber den supervisor modus starten
        # Infos hol ich mir dann ueber get_metadata, koennt ihr aber gerne
        # aendern wennn ihr ne bessere idee habt
        pass

    def get_metadata(self):
        # num of lidars
        # lidar settings
        # lengths/width of environment
        # number of obstacles
        # simulations_speed
        # evtl mehr, ich weiss grad nict was
        # (andere settings die wir nutzen?)

        # TODO for PER: fill config here
        pass

    def reset_environment(self):
        # environment sollte sein wie beim start der simulation
        pass

    def close_environment(self):
        # evlt notwendig, eher nicht :D
        pass


class ExtCtrl():
    def start(self):
        # selbsterklaerend
        # ist es evtl moeglich, den uebertragungsspeed zu aendern?
        # koennte das in Verbindung mit dem Simulationsspeed interessant sein?
        pass

    def close(self):
        # selbsterklaerend
        pass