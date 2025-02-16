
from core.interfaces import GetModelProtocol, LoggerProtocol


class SetModelMixin(LoggerProtocol, GetModelProtocol):
    def set_model(self)->None:
        eps_model, eps_arr = self.get_model()
        self.container.set_model(
            self.temp_var.get(),
            eps_model,
            eps_arr,
        )
        self.logger.info("New model %s (%s) was set", eps_model, eps_arr)
        