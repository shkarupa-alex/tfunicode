#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/op_kernel.h"

using namespace tensorflow;


class CombineSparseSuccessorOp : public OpKernel {
 public:
  explicit CombineSparseSuccessorOp(OpKernelConstruction* ctx) : OpKernel(ctx) {}

  void Compute(OpKernelContext* ctx) override {
    // Prepare source
    const Tensor* parent_indices_tensor;
    OP_REQUIRES_OK(ctx, ctx->input("parent_indices", &parent_indices_tensor));
    const auto parent_indices = parent_indices_tensor->matrix<int64>();
    const uint64 parent_indices_1 = parent_indices_tensor->dim_size(1);

    const Tensor* parent_shape_tensor;
    OP_REQUIRES_OK(ctx, ctx->input("parent_shape", &parent_shape_tensor));
    const auto parent_shape = parent_shape_tensor->vec<int64>();

    const Tensor* child_indices_tensor;
    OP_REQUIRES_OK(ctx, ctx->input("child_indices", &child_indices_tensor));
    const auto child_indices = child_indices_tensor->matrix<int64>();
    OP_REQUIRES(ctx, child_indices_tensor->dim_size(1) == 2,
      errors::InvalidArgument("child indices should correspond to dense rank equals 2"));
    const uint64 child_indices_0 = child_indices_tensor->dim_size(0);

    const Tensor* child_values_tensor;
    OP_REQUIRES_OK(ctx, ctx->input("child_values", &child_values_tensor));
    const auto child_values = child_values_tensor->vec<string>();

    const Tensor* child_shape_tensor;
    OP_REQUIRES_OK(ctx, ctx->input("child_shape", &child_shape_tensor));
    const auto child_shape = child_shape_tensor->vec<int64>();
    OP_REQUIRES(ctx, child_shape_tensor->shape().num_elements() == 2,
      errors::InvalidArgument("child shape should correspond to dense rank equals 2"));


    // Allocate result
    Tensor* result_indices_tensor;
    OP_REQUIRES_OK(
      ctx,
      ctx->allocate_output(
        0,
        TensorShape({(int64)child_indices_tensor->dim_size(0), (int64)(parent_indices_tensor->dim_size(1) + 1)}),
        &result_indices_tensor
      )
    );
    auto result_indices = result_indices_tensor->matrix<int64>();

    Tensor* result_values_tensor;
    OP_REQUIRES_OK(
      ctx,
      ctx->allocate_output(
        1,
        TensorShape({(int64)child_values_tensor->shape().num_elements()}),
        &result_values_tensor
      )
    );
    auto result_values = result_values_tensor->vec<string>();

    Tensor* result_shape_tensor;
    OP_REQUIRES_OK(
      ctx,
      ctx->allocate_output(
        2,
        TensorShape({(int64)(parent_shape_tensor->shape().num_elements() + child_shape_tensor->shape().num_elements() - 1)}),
        &result_shape_tensor
      )
    );
    auto result_shape = result_shape_tensor->vec<int64>();


    // Combine tensors
    for (uint64 c0 = 0; c0 < child_indices_0; c0++) {
      for (uint64 p1 = 0; p1 < parent_indices_1; p1++) {
        result_indices(c0,  p1) = parent_indices(child_indices(c0, 0), p1);
      }
      result_indices(c0, parent_indices_1) = child_indices(c0, 1);
    }

    for (uint64 v = 0; v < (uint64)child_values_tensor->shape().num_elements(); v++) {
      result_values(v) = child_values(v);
    }

    for (uint64 s = 0; s < (uint64)parent_shape_tensor->shape().num_elements(); s++) {
      result_shape(s) = parent_shape(s);
    }
    result_shape(parent_shape_tensor->shape().num_elements()) = child_shape(1);
  }
};

REGISTER_KERNEL_BUILDER(Name("CombineSparseSuccessor").Device(DEVICE_CPU), CombineSparseSuccessorOp);
