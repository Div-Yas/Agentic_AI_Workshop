// backend/models/contractModel.js
const mongoose = require("mongoose");
const { Schema } = mongoose;

const SalaryComponentSchema = new Schema({
    basic_salary: { type: Number, default: 0 },
    hra: { type: Number, default: 0 },
    lta: { type: Number, default: 0 },
    variable_pay: { type: Number, default: 0 },
    bonuses: { type: Number, default: 0 },
    other_allowances: { type: Number, default: 0 }
});

const ContractSchema = new Schema({
    employee_id: String,
    employee_name: String,
    designation: String,
    department: String,
    join_date: Date,
    salary_components: SalaryComponentSchema,
    statutory_obligations: [String],
    region: String,
    currency: String,
    uploaded_at: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model("Contract", ContractSchema);