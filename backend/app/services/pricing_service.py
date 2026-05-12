class PricingService:

    BASE_FEE = 1000
    STAMP_FEE = 500

    @staticmethod
    def calculate():
        return PricingService.BASE_FEE + PricingService.STAMP_FEE