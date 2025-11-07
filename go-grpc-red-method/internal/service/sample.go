package service

import (
	"context"
	"fmt"
	"math/rand"
	"sync"
	"time"

	pb "github.com/nissy-dev/sandbox/go-grpc-red-method/proto/gen/go/proto"

	grpc_codes "google.golang.org/grpc/codes"
	grpc_status "google.golang.org/grpc/status"
)

type SampleService struct {
	mu    sync.RWMutex
	users map[string]*pb.User

	pb.UnimplementedSampleServiceServer
}

func NewSampleService() *SampleService {
	return &SampleService{
		users: make(map[string]*pb.User),
	}
}

func (s *SampleService) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// ランダムに InternalError を返す
	if rand.Intn(10) < 2 {
		return nil, grpc_status.Errorf(grpc_codes.Internal, "internal error occurred")
	}

	user, ok := s.users[req.Id]
	if !ok {
		return nil, grpc_status.Errorf(grpc_codes.NotFound, "user not found")
	}
	return &pb.GetUserResponse{User: user}, nil
}

func (s *SampleService) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// ランダムに InternalError を返す
	if rand.Intn(10) < 2 {
		return nil, grpc_status.Errorf(grpc_codes.Internal, "internal error occurred")
	}

	// ランダムに sleep して遅延を発生させる
	if rand.Intn(10) < 5 {
		time.Sleep(time.Duration(rand.Intn(1000)) * time.Millisecond)
	}

	user := &pb.User{
		Id:   fmt.Sprintf("%d", rand.Intn(1000)),
		Name: req.Name,
	}
	s.users[user.Id] = user
	return &pb.CreateUserResponse{User: user}, nil
}
