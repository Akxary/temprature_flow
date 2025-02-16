

from core.interfaces import SpecContainerProtocol


class GetModelMixin(SpecContainerProtocol):
    def get_model(self)->tuple[tuple[int, ...], tuple[float, ...]]:
        eps_arr = [self.e0_var.get()]
        eps_model = [self.e0_var.get()]
        if self.e1_check_var.get():
            eps_arr.append(self.e1_var.get())
            eps_model.append(1)
        if self.e2_check_var.get():
            eps_arr.append(self.e2_var.get())
            eps_model.append(2)
        return tuple(eps_model), tuple(eps_arr)
    